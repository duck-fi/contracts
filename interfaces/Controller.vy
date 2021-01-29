# @version ^0.2.0


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@view
@external
def reapers(_index: uint256) -> address:
    return ZERO_ADDRESS


@view
@external
def lastReaperIndex() -> uint256:
    return 0


@view
@external
def indexByReaper(_reaper: address) -> uint256:
    return 0


@external
def addReaper(_reaper: address):
    pass


@external
def removeReaper(_reaper: address):
    pass