# @version ^0.2.11
"""
@title Boosting Controller
@author Dispersion Finance Team
@license MIT
"""

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Controller as Controller
import interfaces.BoostingController as BoostingController
import interfaces.GasToken as GasToken
import interfaces.WhiteList as WhiteList


implements: Ownable
implements: BoostingController


struct BoostInfo:
    targetAmount: uint256
    instantAmount: uint256
    warmupTime: uint256
    finishTime: uint256


event Boost:
    account: address
    amount: uint256
    lockTime: uint256

event Unboost:
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
WARMUP_TIME: constant(uint256) = 2 * WEEK


owner: public(address)
futureOwner: public(address)

gasTokenCheckList: public(address)
contractCheckList: public(address)
boostingToken: public(address)
boostIntegral: public(uint256)
lastBoostTimestamp: public(uint256)
boosts: public(HashMap[address, BoostInfo]) # account -> boostInfo
boostIntegralFor: public(HashMap[address, uint256]) # account -> integrated votes
totalBoostIntegralFor: public(HashMap[address, uint256]) # account -> total integrated votes
boostFactorIntegralFor: public(HashMap[address, uint256]) # account -> integrated boost factor * 10e18
lastBoostTimestampFor: public(HashMap[address, uint256]) # account -> last boost timestamp
balances: public(HashMap[address, uint256]) # account -> amount
totalBalance: public(uint256)


@external
def __init__(_gasTokenCheckList: address):
    """
    @notice Contract constructor
    """
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"

    self.gasTokenCheckList = _gasTokenCheckList
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert WhiteList(self.gasTokenCheckList).check(_gasToken), "unsupported gas token" 
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
def _updateBoostIntegral() -> uint256:
    _boostIntegral: uint256 = self.boostIntegral
    _lastBoostTimestamp: uint256 = self.lastBoostTimestamp

    if block.timestamp <= _lastBoostTimestamp:
        return _boostIntegral

    self.lastBoostTimestamp = block.timestamp

    if _lastBoostTimestamp > 0:
        _boostIntegral += self.totalBalance * (block.timestamp - _lastBoostTimestamp)
        self.boostIntegral = _boostIntegral
    
    return _boostIntegral


@internal
def _updateAccountBoostIntegral(_account: address) -> uint256:
    _accountBoostIntegral: uint256 = self.boostIntegralFor[_account]
    _boost: BoostInfo = self.boosts[_account]

    if _boost.finishTime == 0:
        self.boosts[_account].instantAmount = 0
        self.lastBoostTimestampFor[_account] = block.timestamp
        return _accountBoostIntegral

    _lastBoostTimestamp: uint256 = self.lastBoostTimestampFor[_account]
    if _boost.warmupTime > block.timestamp:
        # 2. its during warmup
        # 2.1 calc current user integral
        _instantAmount: uint256 = self._calcAmount(_boost.instantAmount, _boost.targetAmount, _lastBoostTimestamp, _boost.warmupTime, block.timestamp)
        _accountBoostIntegral += (_instantAmount + _boost.instantAmount) * (block.timestamp - _lastBoostTimestamp) / 2
        self.boosts[_account].instantAmount = _instantAmount
        self.boostIntegralFor[_account] = _accountBoostIntegral
        self.lastBoostTimestampFor[_account] = block.timestamp
        return _accountBoostIntegral
    
    if self.boosts[_account].finishTime > block.timestamp:
        # 3. its during max boost
        # 3.1 need to calc user ascending integral (if not calculated yet)
        if _lastBoostTimestamp < _boost.warmupTime:
            _accountBoostIntegral += (_boost.instantAmount + _boost.targetAmount) * (_boost.warmupTime - _lastBoostTimestamp) / 2
            _boost.instantAmount = _boost.targetAmount
            _lastBoostTimestamp = _boost.warmupTime

        # 3.2 need to calc user const integral
        _instantAmount: uint256 = _boost.targetAmount
        _accountBoostIntegral += _instantAmount * (block.timestamp - _lastBoostTimestamp)
        self.boosts[_account].instantAmount = _instantAmount
        self.boostIntegralFor[_account] = _accountBoostIntegral
        self.lastBoostTimestampFor[_account] = block.timestamp

        return _accountBoostIntegral

    # 4. its after boost
    # 4.1 need to calc user ascending integral (if not calculated yet)
    if _lastBoostTimestamp < _boost.warmupTime:
        _accountBoostIntegral += (_boost.instantAmount + _boost.targetAmount) * (_boost.warmupTime - _lastBoostTimestamp) / 2
        _boost.instantAmount = _boost.targetAmount
        _lastBoostTimestamp = _boost.warmupTime

    # 4.2 need to calc user const integral (if not calculated yet)
    if _lastBoostTimestamp < _boost.finishTime:
        _accountBoostIntegral += _boost.targetAmount * (_boost.finishTime - _lastBoostTimestamp)
        _boost.instantAmount = _boost.targetAmount
        _lastBoostTimestamp = _boost.finishTime
    
    # 4.3 need to calc user ZERO const integral
    self.boostIntegralFor[_account] = _accountBoostIntegral
    self.boosts[_account].instantAmount = 0
    self.lastBoostTimestampFor[_account] = block.timestamp
    
    return _accountBoostIntegral

debug1:public(uint256)
debug2:public(uint256)
debug3:public(uint256)
@internal
def _updateAccountBoostFactorIntegral(_account: address) -> uint256:
    self.debug1 = 1
    self.debug2 = 1
    self.debug3 = 1
    # _lastBoostTimestamp: uint256 = self.lastBoostTimestamp
    _lastBoostTimestampFor: uint256 = self.lastBoostTimestampFor[_account]
    _lastBoostIntegralFor: uint256 = self.boostIntegralFor[_account]
    _lastTotalBoostIntegralFor: uint256 = self.totalBoostIntegralFor[_account]
    _newBoostIntegral: uint256 = self._updateBoostIntegral()
    _newAccountBoostIntegral: uint256 = self._updateAccountBoostIntegral(_account)

    if _lastBoostTimestampFor == 0:
        self.debug1 = 12
        self.totalBoostIntegralFor[_account] = _lastTotalBoostIntegralFor
        return 0

    _newBoostFactorIntegralFor: uint256 = self.boostFactorIntegralFor[_account]
    if _newBoostIntegral <= _lastTotalBoostIntegralFor:
        self.debug2=13
        return _newBoostFactorIntegralFor

    _newBoostFactorIntegralFor += (_newAccountBoostIntegral - _lastBoostIntegralFor) * MULTIPLIER * (block.timestamp - _lastBoostTimestampFor) / (_newBoostIntegral - _lastTotalBoostIntegralFor) 
    self.debug3 = _newBoostFactorIntegralFor
    self.boostFactorIntegralFor[_account] = _newBoostFactorIntegralFor
    self.boostIntegralFor[_account] = _newAccountBoostIntegral
    self.totalBoostIntegralFor[_account] = _lastTotalBoostIntegralFor

    return _newBoostFactorIntegralFor


@external
@nonreentrant('lock')
def boost(_amount: uint256, _lockTime: uint256, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Boost reward using boost tokens with amount `_amount` for user `msg.sender`
    @param _amount Amount which is used to boost
    @param _lockTime Time for locking boost tokens
    @param _gasToken Gas token for tx cost reduction
    """
    _gasStart: uint256 = msg.gas
    _boostingToken: address = self.boostingToken
    assert _lockTime >= WARMUP_TIME, "locktime is too short"

    if msg.sender != tx.origin:
        assert WhiteList(self.contractCheckList).check(msg.sender), "contract should be in white list"

    self._updateAccountBoostFactorIntegral(msg.sender)
    # self._updateBoostIntegral()
    # self._updateAccountBoostIntegral(msg.sender)
    self.balances[msg.sender] += _amount
    self.totalBalance +=_amount
    
    _boost: BoostInfo = self.boosts[msg.sender]
    self.boosts[msg.sender].targetAmount = _boost.targetAmount + _amount
    self.boosts[msg.sender].warmupTime = block.timestamp + WARMUP_TIME
    self.boosts[msg.sender].finishTime = max(block.timestamp + _lockTime, _boost.finishTime + _lockTime)
    
    assert ERC20(_boostingToken).transferFrom(msg.sender, self, _amount)
    log Boost(msg.sender, _amount, _lockTime)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 3)


@external
@nonreentrant('lock')
def unboost(_gasToken: address = ZERO_ADDRESS):
    """
    @notice Unboost for account `msg.sender` and withdraw all available boost tokens
    @dev Only possible with unlocked amount, withdraw all amount
    @param _gasToken Gas token for tx cost reduction
    """
    assert self.boosts[msg.sender].finishTime < block.timestamp, "tokens are locked"
    
    _gasStart: uint256 = msg.gas
    _amount: uint256 = self.balances[msg.sender]
    self._updateAccountBoostFactorIntegral(msg.sender)
    # self._updateBoostIntegral()
    # self._updateAccountBoostIntegral(msg.sender)
    self.totalBalance -= _amount
    self.balances[msg.sender] = 0
    self.boosts[msg.sender].targetAmount = 0
    self.boosts[msg.sender].instantAmount = 0
    self.boosts[msg.sender].warmupTime = 0
    self.boosts[msg.sender].finishTime = 0

    assert ERC20(self.boostingToken).transfer(msg.sender, _amount)
    log Unboost(msg.sender, _amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 1)


@view
@external
def availableToUnboost(_account: address) -> uint256:
    """
    @notice Check for available withdrawal amount for account `_account`
    @param _account Account who is unboosting
    @return Unlocked amount to withdraw
    """
    if self.boosts[_account].finishTime >= block.timestamp:
        return 0
    
    return self.balances[_account]


# @external
# def accountBoostIntegral(_account: address) -> uint256:
#     """
#     @notice Returns current boost integral for account `_account`
#     @param _account Account to get its boost integral for
#     @return Account boost integral
#     """
#     return self._updateAccountBoostIntegral(_account)


@external
def updateAccountBoostFactorIntegral(_account: address) -> uint256:
    return self._updateAccountBoostFactorIntegral(_account)


# @external
# def updateBoostIntegral() -> uint256:
#     """
#     @notice Returns common boost integral
#     @return Common boost integral
#     """
#     return self._updateBoostIntegral()


@external
def setBoostingToken(_boostingToken: address):
    assert msg.sender == self.owner, "owner only"
    assert _boostingToken != ZERO_ADDRESS, "zero address"
    assert self.boostingToken == ZERO_ADDRESS, "set only once"
    self.boostingToken = _boostingToken


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Transfers ownership by setting new owner `_futureOwner` candidate
    @dev Callable by `owner` only. Emit CommitOwnership event with `_futureOwner`
    @param _futureOwner Future owner address
    """
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies transfer ownership
    @dev Callable by `owner` only. Function call actually changes `owner`. 
        Emits ApplyOwnership event with `_owner`
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
