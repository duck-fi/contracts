# @version ^0.2.0


@external
def invest(): 
    pass


@external
def reap(): 
    pass


@view
@external
def boost_rate() -> uint256:
    pass


@external
def deposit(amount: uint256, account: address) -> uint256: 
    pass


@external
def withdraw(amount: uint256, account: address) -> uint256: 
    pass
