# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.strategies.ReaperStrategy as ReaperStrategy
import interfaces.Staker as Staker
import interfaces.Ownable as Ownable


implements: Ownable
implements: ReaperStrategy


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


reaper: public(address)
staker: public(address)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_reaper: address, _staker: address):
    self.reaper = _reaper
    self.staker = _staker
    self.owner = msg.sender


@external
def invest(_amount: uint256):
    assert msg.sender == self.reaper, "reaper only"
    _staker: address = self.staker
    ERC20(Staker(_staker).stakeToken()).transferFrom(self.reaper, _staker, _amount)
    Staker(_staker).stake(_amount)


@external
def reap() -> uint256:
    assert msg.sender == self.reaper, "reaper only"
    return Staker(self.staker).claim(self.reaper)


@external
def deposit(_amount: uint256):
    assert msg.sender == self.reaper, "reaper only"
    _staker: address = self.staker
    ERC20(Staker(_staker).stakeToken()).transferFrom(self.reaper, _staker, _amount)
    Staker(_staker).stake(_amount)


@external
def withdraw(_amount: uint256, _account: address):
    assert msg.sender == self.reaper, "reaper only"
    Staker(self.staker).unstake(_amount, _account)


@view
@external
def availableToDeposit(_amount: uint256, _account: address) -> uint256:
    return _amount


@view
@external
def availableToWithdraw(_amount: uint256, _account: address) -> uint256:
    return _amount


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