# @version ^0.2.0


@view
@external
def index_by_reaper(reaper: address) -> uint256:
    pass


@view
@external
def last_reaper_index() -> uint256:
    pass


@view
@external
def reapers(index: uint256) -> address:
    pass


@external
def toggleApprove(account: address): 
    pass


@external
def mint(reaper: address): 
    pass


@external
def minter() -> address: 
    pass
