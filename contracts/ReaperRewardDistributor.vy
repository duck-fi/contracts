# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.ReaperRewardDistributor as ReaperRewardDistributor
import interfaces.Reaper as Reaper
import interfaces.GasToken as GasToken
import interfaces.GasReducible as GasReducible


implements: Ownable
implements: ReaperRewardDistributor
implements: GasReducible


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


MIN_GAS_CONSTANT: constant(uint256) = 21_000


reaper: public(address)
lastBalance: public(HashMap[address, uint256])
rewardIntegral: public(HashMap[address, uint256])
rewardIntegralFor: public(HashMap[address, HashMap[address, uint256]])
reapIntegralFor: public(HashMap[address, HashMap[address, uint256]])
totalReapIntegralFor: public(HashMap[address, HashMap[address, uint256]])
claimAllowance: public(HashMap[address, HashMap[address, HashMap[address, bool]]])
gasTokens: public(HashMap[address, bool])

owner: public(address)
futureOwner: public(address)


@external
def __init__(_reaper: address):
    assert _reaper != ZERO_ADDRESS, "reaper is not set"
    self.reaper = _reaper
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        pass

    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
def claimApprove(_coin: address, _claimer: address, _canClaim: bool):
    self.claimAllowance[_coin][msg.sender][_claimer] = _canClaim


@internal
def _claim(_coin: address, _account: address, _recipient: address):
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
    ERC20(_coin).transfer(_recipient, _rewardDiff * (_reapIntegralFor - self.reapIntegralFor[_coin][_account]) / (_reapIntegral - self.totalReapIntegralFor[_coin][_account]))

    self.reapIntegralFor[_coin][_account] = _reapIntegralFor
    self.totalReapIntegralFor[_coin][_account] = _reapIntegral
    self.rewardIntegralFor[_coin][_account] = _rewardIntegral


@external
def claim(_coin: address, _account: address, _gasToken: address = ZERO_ADDRESS):
    assert _gasToken == ZERO_ADDRESS or self.gasTokens[_gasToken], "unsupported gas token"

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.claimAllowance[_coin][_account][msg.sender], "claim is not allowed"
    self._claim(_coin, _account, _account)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 3)


@external
def claimableTokens(_coin: address, _account: address) -> uint256:
    _rewardDiff: uint256 = self.rewardIntegral[_coin] - self.rewardIntegralFor[_coin][_account]
    _balance: uint256 = ERC20(_coin).balanceOf(self)
    _lastBalance: uint256 = self.lastBalance[_coin]
    if _balance > _lastBalance:
        _rewardDiff += _balance - _lastBalance

    _reaper: address = self.reaper
    Reaper(_reaper).snapshot(_account, ZERO_ADDRESS)
    _reapDiff: uint256 = Reaper(_reaper).reapIntegralFor(_account) - self.reapIntegralFor[_coin][_account]
    _totalReapDiff: uint256 = Reaper(_reaper).reapIntegral() - self.totalReapIntegralFor[_coin][_account]

    return _rewardDiff * _reapDiff / _totalReapDiff


@external
def setGasToken(_gasToken: address, _value: bool):
    assert msg.sender == self.owner, "owner only"
    assert _gasToken != ZERO_ADDRESS, "_gasToken is not set"
    
    self.gasTokens[_gasToken] = _value


@external
def emergencyWithdraw(_coin: address):
    assert msg.sender == self.owner, "owner only"
    assert ERC20(_coin).transfer(self.owner, ERC20(_coin).balanceOf(self))


@external
def claimAdminFee(_coin: address, _gasToken: address = ZERO_ADDRESS):
    assert msg.sender == self.owner, "owner only"
    assert _gasToken == ZERO_ADDRESS or self.gasTokens[_gasToken], "unsupported gas token"

    _gasStart: uint256 = msg.gas

    self._claim(_coin, self.reaper, msg.sender)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@external
def transferOwnership(_futureOwner: address):
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
