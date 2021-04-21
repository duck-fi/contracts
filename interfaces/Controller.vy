# @version ^0.2.11


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@view
@external
def votingController() -> address:
    return ZERO_ADDRESS


@view
@external
def boostingController() -> address:
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


@external
def claimAdminFee(_reaper: address, _gasToken: address):
    pass


@external
def setVotingController(_votingController: address):
    pass


@external
def setBoostingController(_boostingController: address):
    pass
