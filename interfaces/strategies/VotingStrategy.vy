# @version ^0.2.0


@view
@external
def votingController() -> address: 
    return ZERO_ADDRESS


@view
@external
def coinToVotes(_amount: uint256) -> uint256: 
    return 0


@view
@external
def availableToVote(_account: address, _amount: uint256) -> uint256: 
    return 0


@view
@external
def availableToUnvote(_account: address, _amount: uint256) -> uint256: 
    return 0


@external
def vote(_account: address, _amount: uint256) -> uint256: 
    return 0


@external
def unvote(account: address, amount: uint256) -> uint256: 
    return 0
