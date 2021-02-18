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
    reaper: address
    coin: address
    account: address
    amount: uint256

event Unboost:
    reaper: address
    coin: address
    account: address
    amount: uint256

event BoostApproval:
    reaper: address
    coin: address
    ownerAccount: address
    boosterAccount: address
    canBoost: bool

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MULTIPLIER: constant(uint256) = 10 ** 18
MIN_GAS_CONSTANT: constant(uint256) = 21_000
DAY: constant(uint256) = 86_400
WEEK: constant(uint256) = 7 * DAY
BOOST_WEAKNESS: constant(uint256) = 5 * 10 ** 17


owner: public(address)
futureOwner: public(address)

controller: public(address)
farmToken: public(address)
farmTokenRate: public(uint256)
boostingToken: public(address)
boostingTokenRate: public(uint256)
boostingTokenRateAmplifier: public(uint256)

balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> amount

totalBoosts: public(uint256)
boostIntegral: public(uint256)
lastBoostTimestamp: public(uint256)

boosts: public(HashMap[address, BoostInfo]) # account -> boostInfo
boostIntegralFor: public(HashMap[address, uint256]) # account -> integrated votes
lastBoostTimestampFor: public(HashMap[address, uint256]) # account -> last boost timestamp

lockingPeriod: public(uint256)
warmupTime: public(uint256)

coinBalances: public(HashMap[address, uint256]) # coin -> balance

boostAllowance: public(HashMap[address, HashMap[address, HashMap[address, HashMap[address, bool]]]]) # reaper -> coin -> owner -> voter -> canBoost
gasTokens: public(HashMap[address, bool])


@external
def __init__(_controller: address, _farmToken: address, _boostingToken: address):
    """
    @notice Contract constructor
    """
    self.controller = _controller
    self.farmToken = _farmToken
    self.farmTokenRate = 1
    self.boostingToken = _boostingToken
    self.boostingTokenRate = 2
    self.boostingTokenRateAmplifier = 2
    self.warmupTime = 2 * WEEK
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

    delta: uint256 = 0

    if pointA > pointB:
        delta = pointA - pointB
    else:
        delta = pointB - pointA
    
    return (t - tsA) * delta / (tsB - tsA)


@internal
def _updateBoostIntegral():
    # update common intergal
    # if self.lastBoostTimestamp > 0:
    #     self.boostIntegral = self.boostIntegral + self.totalBoosts * (block.timestamp - self.lastBoostTimestamp)
    # self.totalBoosts += _amount
    # self.lastBoostTimestamp = block.timestamp
    pass


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
        
        # 3.2 need to calc user descending integral
        _instantAmount: uint256 = self._calcAmount(self.boosts[_account].instantAmount, self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER, self.lastBoostTimestampFor[_account], self.boosts[_account].warmupTime, block.timestamp)
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (_instantAmount + self.boosts[_account].instantAmount) * (block.timestamp - self.boosts[_account].warmupTime) / 2
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
def boost(_reaper: address, _coin: address, _amount: uint256, _lockTime: uint256, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Boost reward in reaper `_reaper` using tokens `_coin` with amount `_amount` for user `_account`
    @param _reaper Reaper to boost in
    @param _coin Coin which is used to boost
    @param _amount Amount which is used to boost
    @param _account Account who is being boosted
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    assert _amount > 0, "amount must be greater 0"
    assert _coin == self.farmToken or _coin == self.boostingToken, "invalid coin"
    assert _lockTime > self.warmupTime, "locktime is too short"

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.boostAllowance[_reaper][_coin][_account][msg.sender], "boosting approve required"

    self._updateBoostIntegral()

    self.balances[_reaper][_coin][_account] += _amount
    self.coinBalances[_coin] +=_amount
    
    _tokenRate: uint256 = self.farmTokenRate
    if _coin == self.boostingToken:
        _tokenRate = self.boostingTokenRate

    self._updateAccountBoostIntegral(_account)

    self.boosts[_account].targetAmount += _amount * _tokenRate
    self.boosts[_account].warmupTime = block.timestamp + self.warmupTime
    self.boosts[_account].finishTime = max(self.boosts[_account].warmupTime + _lockTime, self.boosts[_account].finishTime + _lockTime)
    
    ERC20(_coin).transferFrom(_account, self, _amount)

    log Boost(_reaper, _coin, _account, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 6)


@external
@nonreentrant('lock')
def unboost(_reaper: address, _coin: address, _amount: uint256, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Unboost for reaper `_reaper` and withdraw tokens `_coin` with amount `_amount` for `_account`
    @dev Only possible with unlocked amount
    @param _reaper Reaper to unboost for
    @param _coin Coin which is used to unboost
    @param _amount Amount which is used to unboost
    @param _account Account who is unboosting
    """
    assert _amount > 0, "amount should be > 0"

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.boostAllowance[_reaper][_coin][_account][msg.sender], "boosting approve required"

    assert self.balances[_reaper][_coin][_account] >= _amount, "insufficiend funds"
    assert self.boosts[_account].finishTime < block.timestamp, "tokens are locked"

    self._updateBoostIntegral()
    self._updateAccountBoostIntegral(_account)

    self.balances[_reaper][_coin][_account] -= _amount
    self.coinBalances[_coin] -= _amount
    
    # TODO: unboost all or partially reduction
    self.boosts[_account].targetAmount = 0
    self.boosts[_account].instantAmount = 0
    self.boosts[_account].warmupTime = 0
    self.boosts[_account].finishTime = 0

    ERC20(_coin).transfer(_account, _amount)
    
    log Unboost(_reaper, _coin, _account, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 5)


@view
@external
def availableToUnboost(_reaper: address, _coin: address, _account: address) -> uint256:
    """
    @notice Check for available withdrawal amount from reaper `_reaper` for tokens `_coin` for account `_account`
    @param _reaper Reaper to unboost for
    @param _coin Coin which is used to unboost
    @param _account Account who is unboosting
    @return Unlocked amount to withdraw
    """
    if self.boosts[_account].finishTime >= block.timestamp:
        return 0
    
    return self.balances[_reaper][_coin][_account]


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


# TODO: need this?
# # @view
# # @external
# # def accountVotePower(_reaper: address, _coin: address, _account: address) -> uint256:
# #     """
# #     @notice Returns vote power share for account `_account` for reaper `_reaper` multiplied on 1e18
# #     @param _reaper Reaper to get its vote power for
# #     @param _coin Coin which has been used to vote
# #     @param _account Account to get its vote power for
# #     @return Vote power multiplied on 1e18
# #     """
# #     if self.strategyByCoin[_coin] == ZERO_ADDRESS:
# #         return 0
    
# #     return VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.balances[_reaper][_coin][_account])


@external
def boostApprove(_reaper: address, _coin: address, _booster: address, _canBoost: bool):
    """
    @notice Allows to perform boosts and unboosts for reaper `_reaper` in tokens `_coin` for `_booster` instead of msg.sender by setting `_canBoost` param
    @param _reaper Reaper to approve boosting for
    @param _coin Coin which is used to approve boosting
    @param _booster Account who can do boosting or unboosting instead of msg.sender
    @param _canBoost Possibility of boosting or unboosting
    """
    self.boostAllowance[_reaper][_coin][msg.sender][_booster] = _canBoost

    log BoostApproval(_reaper, _coin, msg.sender, _booster, _canBoost)


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
