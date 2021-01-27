# @version ^0.2.0


@view
@external
def index_by_reaper(reaper: address) -> uint256:
    return 0


@view
@external
def last_reaper_index() -> uint256:
    return 0


@view
@external
def reapers(index: uint256) -> address:
    return ZERO_ADDRESS


@external
def toggleApprove(account: address): 
    pass


@external
def mint(reaper: address): 
    pass


@external
def minter() -> address: 
    return ZERO_ADDRESS
