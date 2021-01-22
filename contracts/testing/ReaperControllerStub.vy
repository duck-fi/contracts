# @version ^0.2.0

import interfaces.ReaperController as ReaperController


implements: ReaperController


reapers: public(address[10 ** 3])
index_by_reaper: public(HashMap[address, uint256])
last_reaper_index: public(uint256)


@external
def __init__():
    pass


@view
@external
def reaper_by_index(reaper: address) -> uint256:
    return 0


@external
def toggleApprove(account: address): 
    pass


@external
def mint(reaper: address): 
    pass


@external
def minter() -> address: 
    return ZERO_ADDRESS


@external
@nonreentrant('lock')
def addReaper(reaper: address):
    reaper_index: uint256 = self.index_by_reaper[reaper]
    assert reaper_index == 0, "reaper exists"

    new_reaper_index: uint256 = self.last_reaper_index + 1
    self.reapers[new_reaper_index] = reaper
    self.index_by_reaper[reaper] = new_reaper_index
    self.last_reaper_index = new_reaper_index
