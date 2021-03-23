# @version ^0.2.0


@view
@external
def reaper() -> address: 
    return ZERO_ADDRESS


@external
def invest(_amount: uint256):
    pass


@external
def reap() -> uint256:
    return 0


@view
@external
def availableToDeposit(_amount: uint256, _account: address) -> uint256:
    return 0


@view
@external
def availableToWithdraw(_amount: uint256, _account: address) -> uint256:
    return 0


@external
def deposit(_amount: uint256):
    pass


@external
def withdraw(_amount: uint256, _account: address):
    pass


@external
def claim(_amount: uint256, _account: address):
    pass
