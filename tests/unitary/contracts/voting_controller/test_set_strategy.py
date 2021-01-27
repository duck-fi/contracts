#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=10**3))
def test_set_strategy(voting_controller, farm_token, usdn_token, three_reapers_stub, voting_strategy_stub, voting_strategy_stub_v2, ZERO_ADDRESS, neo, morpheus, amount):
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert voting_controller.strategies(usdn_token) == ZERO_ADDRESS

    with brownie.reverts("invalid strategy"):
        voting_controller.setStrategy(farm_token, ZERO_ADDRESS, {'from': neo})

    with brownie.reverts("invalid strategy"):
        voting_controller.setStrategy(usdn_token, ZERO_ADDRESS, {'from': neo})

    with brownie.reverts("unauthorized"):
        voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': morpheus})
    
    with brownie.reverts("unauthorized"):
        voting_controller.setStrategy(usdn_token, voting_strategy_stub, {'from': morpheus})

    # try to vote with farm_token (it fails)
    initial_balance = farm_token.balanceOf(neo)
    farm_token.approve(voting_controller, amount, {'from': neo})
    with brownie.reverts("invalid params"):
        voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': neo})

    assert voting_controller.index_by_coin(farm_token) == 0
    assert voting_controller.index_by_coin(usdn_token) == 0
    assert voting_controller.last_coin_index() == 0
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == ZERO_ADDRESS
    assert voting_controller.coins(2) == ZERO_ADDRESS
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert voting_controller.strategies(usdn_token) == ZERO_ADDRESS

    # now add strategy with farm_token
    voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': neo})
    assert voting_controller.index_by_coin(farm_token) == 1
    assert voting_controller.index_by_coin(usdn_token) == 0
    assert voting_controller.last_coin_index() == 1
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == farm_token
    assert voting_controller.coins(2) == ZERO_ADDRESS
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == voting_strategy_stub
    assert voting_controller.strategies(usdn_token) == ZERO_ADDRESS

    # try to vote with farm_token (success)
    voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': neo})
    assert farm_token.balanceOf(voting_controller) == amount
    assert farm_token.balanceOf(neo) == initial_balance - amount

    # now add another strategy with usdn_token
    voting_controller.setStrategy(usdn_token, voting_strategy_stub, {'from': neo})
    assert voting_controller.index_by_coin(farm_token) == 1
    assert voting_controller.index_by_coin(usdn_token) == 2
    assert voting_controller.last_coin_index() == 2
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == farm_token
    assert voting_controller.coins(2) == usdn_token
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == voting_strategy_stub
    assert voting_controller.strategies(usdn_token) == voting_strategy_stub

    # set up usdn_token for voting
    usdn_token.deposit(neo, initial_balance, {'from': neo})
    usdn_token.approve(voting_controller, amount, {'from': neo})

    # try to vote with usdn_token
    voting_controller.vote(three_reapers_stub[1], usdn_token, amount, {'from': neo})
    assert usdn_token.balanceOf(voting_controller) == amount
    assert usdn_token.balanceOf(neo) == initial_balance - amount

    # check for vote shares
    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 5 * 10 ** 17
    assert voting_controller.accountVotePower(three_reapers_stub[0], farm_token, neo) == amount
    assert voting_controller.accountVotePower(three_reapers_stub[1], usdn_token, neo) == amount

    # remove farm_token strategy
    voting_controller.setStrategy(farm_token, ZERO_ADDRESS, {'from': neo})
    assert voting_controller.index_by_coin(farm_token) == 0
    assert voting_controller.index_by_coin(usdn_token) == 1
    assert voting_controller.last_coin_index() == 1
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == usdn_token
    assert voting_controller.coins(2) == ZERO_ADDRESS
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert voting_controller.strategies(usdn_token) == voting_strategy_stub

    # check for vote shares
    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 0
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 10 ** 18
    assert voting_controller.accountVotePower(three_reapers_stub[0], farm_token, neo) == 0
    assert voting_controller.accountVotePower(three_reapers_stub[1], usdn_token, neo) == amount

    # try to unvote with farm_token (success)
    voting_controller.unvote(three_reapers_stub[0], farm_token, amount, {'from': neo})
    assert farm_token.balanceOf(voting_controller) == 0
    assert initial_balance == farm_token.balanceOf(neo)

    # remove usdn_token strategy
    voting_controller.setStrategy(usdn_token, ZERO_ADDRESS, {'from': neo})
    assert voting_controller.index_by_coin(farm_token) == 0
    assert voting_controller.index_by_coin(usdn_token) == 0
    assert voting_controller.last_coin_index() == 0
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == ZERO_ADDRESS
    assert voting_controller.coins(2) == ZERO_ADDRESS
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert voting_controller.strategies(usdn_token) == ZERO_ADDRESS

    # try to unvote with usdn_token (success)
    voting_controller.unvote(three_reapers_stub[1], usdn_token, amount, {'from': neo})
    assert usdn_token.balanceOf(voting_controller) == 0
    assert initial_balance == usdn_token.balanceOf(neo)

    # add strategy with usdn_token again
    voting_controller.setStrategy(usdn_token, voting_strategy_stub_v2, {'from': neo})
    assert voting_controller.index_by_coin(farm_token) == 0
    assert voting_controller.index_by_coin(usdn_token) == 1
    assert voting_controller.last_coin_index() == 1
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == usdn_token
    assert voting_controller.coins(2) == ZERO_ADDRESS
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert voting_controller.strategies(usdn_token) == voting_strategy_stub_v2

    # add strategy with farm_token again
    voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': neo})
    assert voting_controller.index_by_coin(farm_token) == 2
    assert voting_controller.index_by_coin(usdn_token) == 1
    assert voting_controller.last_coin_index() == 2
    assert voting_controller.coins(0) == ZERO_ADDRESS
    assert voting_controller.coins(1) == usdn_token
    assert voting_controller.coins(2) == farm_token
    assert voting_controller.coins(3) == ZERO_ADDRESS
    assert voting_controller.strategies(farm_token) == voting_strategy_stub
    assert voting_controller.strategies(usdn_token) == voting_strategy_stub_v2

    # vote with usdn_token
    usdn_token.approve(voting_controller, amount, {'from': neo})
    voting_controller.vote(three_reapers_stub[0], usdn_token, amount, {'from': neo})
    assert usdn_token.balanceOf(voting_controller) == amount
    assert usdn_token.balanceOf(neo) == initial_balance - amount

    # vote with farm_token
    farm_token.approve(voting_controller, amount, {'from': neo})
    voting_controller.vote(three_reapers_stub[1], farm_token, amount, {'from': neo})
    assert farm_token.balanceOf(voting_controller) == amount
    assert farm_token.balanceOf(neo) == initial_balance - amount

    # check for vote shares
    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 7.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.accountVotePower(three_reapers_stub[0], usdn_token, neo) == 3 * amount # voting_strategy_stub_v2 => amount x3
    assert voting_controller.accountVotePower(three_reapers_stub[1], farm_token, neo) == amount
