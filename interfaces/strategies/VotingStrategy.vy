# @version ^0.2.0


@view
@external
def coinToVotes(amount: uint256) -> uint256: 
    pass


@view
@external
def availableToUnvote(account: address, amount: uint256) -> uint256: 
    pass


@external
def vote(account: address, amount: uint256) -> uint256: 
    pass


@external
def unvote(account: address, amount: uint256) -> uint256: 
    pass