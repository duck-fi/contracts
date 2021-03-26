# @version ^0.2.11
"""
@title Addresses Check List
@author Dispersion Finance Team
@license MIT
"""


import interfaces.Ownable as Ownable
import interfaces.AddressesCheckList as AddressesCheckList


implements: Ownable
implements: AddressesCheckList


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


owner: public(address)
futureOwner: public(address)
get: public(HashMap[address, bool])


@external
def __init__():
    """
    @notice Contract constructor
    """
    self.owner = msg.sender


@external
def set(_key: address, _value: bool):
    assert msg.sender == self.owner, "owner only"
    assert _key != ZERO_ADDRESS, "zero address"
    self.get[_key] = _value


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
