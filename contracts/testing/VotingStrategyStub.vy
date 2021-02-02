# @version ^0.2.0

import interfaces.strategies.VotingStrategy as VotingStrategy


implements: VotingStrategy


@external
def __init__():
    pass


@view
@external
def votingController() -> address: 
    return ZERO_ADDRESS


@view
@external
def coinToVotes(amount: uint256) -> uint256: 
    return amount


@view
@external
def availableToVote(account: address, amount: uint256) -> uint256: 
    return amount


@view
@external
def availableToUnvote(account: address, amount: uint256) -> uint256: 
    return amount


@external
def vote(account: address, amount: uint256) -> uint256: 
    return amount


@external
def unvote(account: address, amount: uint256) -> uint256: 
    return amount
