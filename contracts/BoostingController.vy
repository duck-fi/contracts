# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Controller as Controller
import interfaces.BoostingController as BoostingController
import interfaces.GasToken as GasToken
import interfaces.GasReducible as GasReducible


implements: Ownable
implements: BoostingController
implements: GasReducible


struct BoostInfo:
    targetAmount: uint256
    instantAmount: uint256
    warmupTime: uint256
    finishTime: uint256


event Boost:
    coin: address
    account: address
    amount: uint256

event Unboost:
    coin: address
    account: address
    amount: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MULTIPLIER: constant(uint256) = 10 ** 18
MIN_GAS_CONSTANT: constant(uint256) = 21_000
DAY: constant(uint256) = 86_400
WEEK: constant(uint256) = 7 * DAY
BOOST_WEAKNESS: constant(uint256) = 5 * 10 ** 17 # multiplied on 10 ** 18


owner: public(address)
futureOwner: public(address)

farmToken: public(address)
farmTokenRate: public(uint256)
boostingToken: public(address)
boostingTokenRate: public(uint256)
boostIntegral: public(uint256)
lastBoostTimestamp: public(uint256)
boosts: public(HashMap[address, BoostInfo]) # account -> boostInfo
boostIntegralFor: public(HashMap[address, uint256]) # account -> integrated votes
lastBoostTimestampFor: public(HashMap[address, uint256]) # account -> last boost timestamp
minLockingPeriod: public(uint256)
warmupTime: public(uint256)
balances: public(HashMap[address, HashMap[address, uint256]]) # coin -> account -> amount
coinBalances: public(HashMap[address, uint256]) # coin -> balance
gasTokens: public(HashMap[address, bool])


@external
def __init__(_farmToken: address, _boostingToken: address):
    """
    @notice Contract constructor
    """
    self.farmToken = _farmToken
    self.farmTokenRate = 1
    self.boostingToken = _boostingToken
    self.boostingTokenRate = 2
    self.warmupTime = 2 * WEEK
    self.minLockingPeriod = 2 * WEEK
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert self.gasTokens[_gasToken], "unsupported gas token" 

    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@internal
def _calcAmount(pointA: uint256, pointB: uint256, tsA: uint256, tsB: uint256, t: uint256) -> uint256:
    assert tsB >= tsA, "reverted timestamps"
    assert tsA <= t and t <= tsB, "t not in interval"

    if tsB == tsA:
        return 0

    if pointA <= pointB:
        return (t - tsA) * (pointB - pointA) / (tsB - tsA) + pointA
    else:
        return pointA - (t - tsA) * (pointA - pointB) / (tsB - tsA)


@internal
def _updateBoostIntegral():
    if self.lastBoostTimestamp > 0:
        totalBoost: uint256 = self.coinBalances[self.farmToken] * self.farmTokenRate + self.coinBalances[self.boostingToken] * self.boostingTokenRate
        self.boostIntegral = self.boostIntegral + totalBoost * (block.timestamp - self.lastBoostTimestamp)
    
    self.lastBoostTimestamp = block.timestamp


@internal
def _updateAccountBoostIntegral(_account: address):
    if self.boosts[_account].finishTime == 0:
        self.boosts[_account].instantAmount = 0
        self.lastBoostTimestampFor[_account] = block.timestamp

        return

    if self.boosts[_account].warmupTime > block.timestamp:
        # 2. its during warmup

        # 2.1 calc current user integral
        _instantAmount: uint256 = self._calcAmount(self.boosts[_account].instantAmount, self.boosts[_account].targetAmount, self.lastBoostTimestampFor[_account], self.boosts[_account].warmupTime, block.timestamp)
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (_instantAmount + self.boosts[_account].instantAmount) * (block.timestamp - self.lastBoostTimestampFor[_account]) / 2
        self.boosts[_account].instantAmount = _instantAmount
        self.lastBoostTimestampFor[_account] = block.timestamp

        return
    
    if self.boosts[_account].finishTime > block.timestamp:
        # 3. its during reduction
        
        # 3.1 need to calc user ascending integral (if not calculated yet)
        if self.lastBoostTimestampFor[_account] < self.boosts[_account].warmupTime:
            self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].instantAmount + self.boosts[_account].targetAmount) * (self.boosts[_account].warmupTime - self.lastBoostTimestampFor[_account]) / 2
            self.boosts[_account].instantAmount = self.boosts[_account].targetAmount
            self.lastBoostTimestampFor[_account] = self.boosts[_account].warmupTime

        # 3.2 need to calc user descending integral
        _instantAmount: uint256 = self._calcAmount(self.boosts[_account].instantAmount, self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER, self.lastBoostTimestampFor[_account], self.boosts[_account].finishTime, block.timestamp)
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].instantAmount + _instantAmount) * (block.timestamp - self.lastBoostTimestampFor[_account]) / 2
        self.boosts[_account].instantAmount = _instantAmount
        self.lastBoostTimestampFor[_account] = block.timestamp

        return

    # 4. its after reduction
    # 4.1 need to calc user ascending integral (if not calculated yet)
    if self.lastBoostTimestampFor[_account] < self.boosts[_account].warmupTime:
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].instantAmount + self.boosts[_account].targetAmount) * (self.boosts[_account].warmupTime - self.lastBoostTimestampFor[_account]) / 2
        self.boosts[_account].instantAmount = self.boosts[_account].targetAmount
        self.lastBoostTimestampFor[_account] = self.boosts[_account].warmupTime

    # 4.2 need to calc user descending integral (if not calculated yet)
    if self.lastBoostTimestampFor[_account] < self.boosts[_account].finishTime:
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].instantAmount + self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER) * (self.boosts[_account].finishTime - self.lastBoostTimestampFor[_account]) / 2
        self.boosts[_account].instantAmount = self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER
        self.lastBoostTimestampFor[_account] = self.boosts[_account].finishTime

    # 4.3 need to calc user const integral
    self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + self.boosts[_account].instantAmount * (block.timestamp - self.lastBoostTimestampFor[_account])
    self.lastBoostTimestampFor[_account] = block.timestamp


@external
@nonreentrant('lock')
def boost(_coin: address, _amount: uint256, _lockTime: uint256, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Boost reward using tokens `_coin` with amount `_amount` for user `msg.sender`
    @param _coin Coin which is used to boost
    @param _amount Amount which is used to boost
    @param _lockTime Time for locking boost tokens
    @param _gasToken Gas token for tx cost reduction
    """
    assert _coin == self.farmToken or _coin == self.boostingToken, "invalid coin"
    assert _amount > 0, "zero amount"
    assert _lockTime >= self.minLockingPeriod, "locktime is too short"

    _gasStart: uint256 = msg.gas

    self._updateBoostIntegral()
    self._updateAccountBoostIntegral(msg.sender)

    self.balances[_coin][msg.sender] += _amount
    self.coinBalances[_coin] +=_amount
    
    _tokenRate: uint256 = self.farmTokenRate
    if _coin == self.boostingToken:
        _tokenRate = self.boostingTokenRate


    self.boosts[msg.sender].targetAmount += _amount * _tokenRate
    self.boosts[msg.sender].warmupTime = block.timestamp + self.warmupTime
    self.boosts[msg.sender].finishTime = max(self.boosts[msg.sender].warmupTime + _lockTime, self.boosts[msg.sender].finishTime + _lockTime)
    
    ERC20(_coin).transferFrom(msg.sender, self, _amount)

    log Boost(_coin, msg.sender, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 4)


@external
@nonreentrant('lock')
def unboost(_coin: address, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Unboost for account `msg.sender` and withdraw all available tokens `_coin`
    @dev Only possible with unlocked amount, withdraw all amount
    @param _coin Coin which is used to unboost
    @param _gasToken Gas token for tx cost reduction
    """
    _gasStart: uint256 = msg.gas
    _amount: uint256 = self.balances[_coin][msg.sender]

    assert self.boosts[msg.sender].finishTime < block.timestamp, "tokens are locked"
    assert _amount > 0, "insufficiend funds"

    self._updateBoostIntegral()
    self._updateAccountBoostIntegral(msg.sender)

    self.coinBalances[_coin] -= _amount
    self.balances[_coin][msg.sender] = 0
    
    self.boosts[msg.sender].targetAmount = 0
    self.boosts[msg.sender].instantAmount = 0
    self.boosts[msg.sender].warmupTime = 0
    self.boosts[msg.sender].finishTime = 0

    ERC20(_coin).transfer(msg.sender, _amount)
    
    log Unboost(_coin, msg.sender, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@view
@external
def availableToUnboost(_coin: address, _account: address) -> uint256:
    """
    @notice Check for available withdrawal amount in tokens `_coin` for account `_account`
    @param _coin Coin which is used to unboost
    @param _account Account who is unboosting
    @return Unlocked amount to withdraw
    """
    if self.boosts[_account].finishTime >= block.timestamp:
        return 0
    
    return self.balances[_coin][_account]


@external
def accountBoostIntegral(_account: address) -> uint256:
    """
    @notice Returns current boost integral for account `_account`
    @param _account Account to get its boost integral for
    @return Account boost integral
    """
    self._updateAccountBoostIntegral(_account)
    
    return self.boostIntegralFor[_account]


@external
def commonBoostIntegral() -> uint256:
    """
    @notice Returns common boost integral
    @return Common boost integral
    """
    self._updateBoostIntegral()

    return self.boostIntegral


@external
def setGasToken(_gasToken: address, _value: bool):
    assert msg.sender == self.owner, "owner only"
    assert _gasToken != ZERO_ADDRESS, "_gasToken is not set"
    
    self.gasTokens[_gasToken] = _value


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Sets new future owner address
    @dev Callable by owner only
    @param _futureOwner New future owner address
    """
    assert msg.sender == self.owner, "owner only"

    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies new future owner address as current owner
    @dev Callable by owner only
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
