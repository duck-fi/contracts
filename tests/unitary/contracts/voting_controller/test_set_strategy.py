#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=10**3))
def test_set_strategy(voting_controller, farm_token, three_reapers_stub, voting_strategy_stub, ZERO_ADDRESS, neo, morpheus, amount):
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS

    with brownie.reverts("coin can't be removed"):
        voting_controller.setStrategy(farm_token, ZERO_ADDRESS, {'from': neo})

    with brownie.reverts("unauthorized"):
        voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': morpheus})
    
    # try to vote with farm_token (it fails)
    initial_balance = farm_token.balanceOf(neo)
    farm_token.approve(voting_controller, amount, {'from': neo})
    with brownie.reverts("invalid params"):
        voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': neo})

    voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': neo})
    assert voting_controller.strategies(farm_token) == voting_strategy_stub
    assert voting_controller.coins(farm_token)

    # try to vote with farm_token (success)
    voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': neo})
    assert farm_token.balanceOf(voting_controller) == amount
    assert farm_token.balanceOf(neo) == initial_balance - amount

    voting_controller.setStrategy(farm_token, ZERO_ADDRESS, {'from': neo})
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert not voting_controller.coins(farm_token)

    # try to unvote with farm_token (success)
    voting_controller.unvote(three_reapers_stub[0], farm_token, amount, {'from': neo})
    assert farm_token.balanceOf(voting_controller) == 0
    assert initial_balance == farm_token.balanceOf(neo)
