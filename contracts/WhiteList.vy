# @version ^0.2.11
"""
@title White List
@author Dispersion Finance Team
@license MIT
"""


import interfaces.Ownable as Ownable
import interfaces.WhiteList as WhiteList


implements: Ownable
implements: WhiteList


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


owner: public(address)
futureOwner: public(address)
check: public(HashMap[address, bool])


@external
def __init__():
    """
    @notice Contract constructor
    @dev `owner` = `msg.sender`. 
    """
    self.owner = msg.sender


@external
def addAddress(_account: address):
    """
    @notice Adds address to list for later verification(`check`).
    @dev Callable by `owner` only. `_account` can't be equal `ZERO_ADDRESS`. 
    @param _account Address to add to list
    """
    assert msg.sender == self.owner, "owner only"
    assert _account != ZERO_ADDRESS, "zero address"
    self.check[_account] = True


@external
def removeAddress(_account: address):
    """
    @notice Remove address from list.
    @dev Callable by `owner` only. `_account` can't be equal `ZERO_ADDRESS`.
    @param _account Address to remove from list
    """
    assert msg.sender == self.owner, "owner only"
    assert _account != ZERO_ADDRESS, "zero address"
    self.check[_account] = False


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
