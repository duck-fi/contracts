# @version ^0.2.0

import interfaces.Controller as Controller


implements: Controller


reapers: public(address[10 ** 3])
indexByReaper: public(HashMap[address, uint256])
lastReaperIndex: public(uint256)


@external
def __init__():
    pass


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@external
@nonreentrant('lock')
def addReaper(_reaper: address):
    _reaperIndex: uint256 = self.indexByReaper[_reaper]
    assert _reaperIndex == 0, "reaper exists"

    _newReaperIndex: uint256 = self.lastReaperIndex + 1
    self.reapers[_newReaperIndex] = _reaper
    self.indexByReaper[_reaper] = _newReaperIndex
    self.lastReaperIndex = _newReaperIndex


@external
def removeReaper(_reaper: address):
    pass


@external
def claimAdminFee(_reaper: address):
    pass
