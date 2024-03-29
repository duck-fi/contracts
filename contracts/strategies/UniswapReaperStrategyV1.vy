# @version ^0.2.11
"""
@title Uniswap Reaper Strategy V1
@author Dispersion Finance Team
@license MIT
"""


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
activated: public(bool)
admin: public(address)
owner: public(address)
futureOwner: public(address)


@external
def __init__():
    self.activated = False
    self.owner = msg.sender


@external
def invest(_amount: uint256):
    assert False, "not supported"


@external
def reap() -> uint256:
    assert False, "not supported"
    return 0


@external
def deposit(_amount: uint256):
    pass


@external
def withdraw(_amount: uint256, _account: address):
    assert self.activated, "not activated"


@external
def activate():
    assert msg.sender == self.owner, "owner only"
    assert not self.activated, "activated already"
    self.activated = True


@view
@external
def availableToDeposit(_amount: uint256, _account: address) -> uint256:
    return _amount


@view
@external
def availableToWithdraw(_amount: uint256, _account: address) -> uint256:
    if not self.activated:
        return 0

    return _amount


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
