# @version ^0.2.11
"""
@title Reaper Reward Distributor
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.ReaperRewardDistributor as ReaperRewardDistributor
import interfaces.Reaper as Reaper
import interfaces.GasToken as GasToken
import interfaces.WhiteList as WhiteList


implements: Ownable
implements: ReaperRewardDistributor


event Claim:
    coin: address
    account: address
    amount: uint256

event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


MIN_GAS_CONSTANT: constant(uint256) = 21_000


reaper: public(address)
gasTokenCheckList: public(address)
lastBalance: public(HashMap[address, uint256])
rewardIntegral: public(HashMap[address, uint256])
rewardIntegralFor: public(HashMap[address, HashMap[address, uint256]])
reapIntegralFor: public(HashMap[address, HashMap[address, uint256]])
totalReapIntegralFor: public(HashMap[address, HashMap[address, uint256]])
claimAllowance: public(HashMap[address, HashMap[address, HashMap[address, bool]]])

owner: public(address)
futureOwner: public(address)


@external
def __init__(_reaper: address, _gasTokenCheckList: address):
    """
    @notice Contract constructor
    """
    assert _reaper != ZERO_ADDRESS, "reaper is not set"
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"
    self.reaper = _reaper
    self.gasTokenCheckList = _gasTokenCheckList
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert WhiteList(self.gasTokenCheckList).check(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
def claimApprove(_coin: address, _claimer: address, _canClaim: bool):
    self.claimAllowance[_coin][msg.sender][_claimer] = _canClaim


@internal
def _claim(_coin: address, _account: address, _recipient: address) -> uint256:
    _balance: uint256 = ERC20(_coin).balanceOf(self)
    _lastBalance: uint256 = self.lastBalance[_coin]
    _rewardIntegral: uint256 = self.rewardIntegral[_coin]
    if _balance > _lastBalance:
        _rewardIntegral += _balance - _lastBalance
        self.rewardIntegral[_coin] = _rewardIntegral
    
    _rewardDiff: uint256 = _rewardIntegral - self.rewardIntegralFor[_coin][_account]
    _reaper: address = self.reaper
    Reaper(_reaper).snapshot(_account, ZERO_ADDRESS)
    _reapIntegralFor: uint256 = Reaper(_reaper).reapIntegralFor(_account)
    _reapIntegral: uint256 = Reaper(_reaper).reapIntegral()

    _totalReaperDiff: uint256 = _reapIntegral - self.totalReapIntegralFor[_coin][_account]
    if _totalReaperDiff == 0:
        return 0

    _reap: uint256 = _rewardDiff * (_reapIntegralFor - self.reapIntegralFor[_coin][_account]) / _totalReaperDiff
    assert ERC20(_coin).transfer(_recipient, _reap)

    self.lastBalance[_coin] = _balance - _reap
    self.reapIntegralFor[_coin][_account] = _reapIntegralFor
    self.totalReapIntegralFor[_coin][_account] = _reapIntegral
    self.rewardIntegralFor[_coin][_account] = _rewardIntegral

    return _reap


@external
def claim(_coin: address, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.claimAllowance[_coin][_account][msg.sender], "claim is not allowed"
    
    _amount: uint256 = self._claim(_coin, _account, _account)
    log Claim(_coin, _account, _amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 3)


@view
@external
def claimableTokens(_coin: address, _account: address) -> uint256:
    _balance: uint256 = ERC20(_coin).balanceOf(self)
    _lastBalance: uint256 = self.lastBalance[_coin]
    _rewardIntegral: uint256 = self.rewardIntegral[_coin]
    if _balance > _lastBalance:
        _rewardIntegral += _balance - _lastBalance
    
    _rewardDiff: uint256 = _rewardIntegral - self.rewardIntegralFor[_coin][_account]
    _reaper: address = self.reaper
    _reapIntegralFor: uint256 = Reaper(_reaper).reapIntegralFor(_account)
    _reapIntegral: uint256 = Reaper(_reaper).reapIntegral()

    _totalReaperDiff: uint256 = _reapIntegral - self.totalReapIntegralFor[_coin][_account]
    if _totalReaperDiff == 0:
        return 0

    return _rewardDiff * (_reapIntegralFor - self.reapIntegralFor[_coin][_account]) / _totalReaperDiff


@external
def emergencyWithdraw(_coin: address):
    assert msg.sender == self.owner, "owner only"
    assert ERC20(_coin).transfer(self.owner, ERC20(_coin).balanceOf(self))


@external
def claimAdminFee(_coin: address, _gasToken: address = ZERO_ADDRESS):
    assert msg.sender == self.owner, "owner only"

    _gasStart: uint256 = msg.gas
    _amount: uint256 = self._claim(_coin, self.reaper, msg.sender)
    log Claim(_coin, msg.sender, _amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


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
