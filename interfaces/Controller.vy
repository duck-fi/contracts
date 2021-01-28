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


@view
@external
def minted(_reaper: address, _account: address) -> uint256:
    return 0


@view
@external
def mintAllowance(_reaper: address, _owner: address, _minter: address) -> bool:
    return False


@external
def mint(_reaper: address, _account: address):
    pass


@external
def mintApprove(_reaper: address, _minter: address, _canMint: bool):
    pass


@external
def addReaper(_reaper: address):
    pass


@external
def removeReaper(_reaper: address):
    pass