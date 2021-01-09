# @version ^0.2.0


import interfaces.ReaperStrategy as ReaperStrategy
import interfaces.Ownable as Ownable


implements: Ownable
implements: ReaperStrategy


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


# minter: public(address)
# reapers: public(address[MAX_REAPERS_COUNT])
# index_by_reaper: public(HashMap[address, uint256])
# last_reaper_index: public(uint256)
# minted: public(HashMap[address, HashMap[address, uint256]])
# allowance: public(HashMap[address, HashMap[address, bool]])

owner: public(address)
future_owner: public(address)


@external
def __init__():
    # self.minter = _minter
    self.owner = msg.sender


@external
def deposit(amount: uint256, account: address) -> uint256:
    return amount


@external
def withdraw(amount: uint256, account: address) -> uint256:
    return amount


@external
def transferOwnership(_future_owner: address):
    assert msg.sender == self.owner, "owner only"

    self.future_owner = _future_owner
    log CommitOwnership(_future_owner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.future_owner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)