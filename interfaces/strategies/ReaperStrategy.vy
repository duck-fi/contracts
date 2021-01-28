# @version ^0.2.0


@view
@external
def reaper() -> address: 
    return ZERO_ADDRESS


@view
@external
def staker() -> address:
    return ZERO_ADDRESS


@external
def invest():
    pass


@external
def reap():
    pass


@external
def deposit(_amount: uint256, _account: address) -> uint256:
    return 0


@external
def withdraw(_amount: uint256, _account: address) -> uint256:
    return 0
