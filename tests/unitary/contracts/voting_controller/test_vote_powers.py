#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


DAY = 86400
WEEK = DAY * 7


def test_reaper_vote_share_init(voting_controller, farm_token, three_reapers_stub, neo, morpheus, trinity, thomas):
    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 0
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 0


def test_reaper_vote_share(voting_controller, farm_token, three_reapers_stub, neo, morpheus, trinity, thomas):
    farm_token.transfer(morpheus, 2000, {'from': neo})
    farm_token.transfer(trinity, 2000, {'from': neo})
    farm_token.transfer(thomas, 2000, {'from': neo})
    initial_balance = farm_token.balanceOf(neo)

    farm_token.approve(voting_controller, 2000, {'from': neo})
    farm_token.approve(voting_controller, 2000, {'from': morpheus})
    farm_token.approve(voting_controller, 2000, {'from': trinity})
    farm_token.approve(voting_controller, 2000, {'from': thomas})

    voting_controller.vote(three_reapers_stub[0], farm_token, 10, {'from': neo})
    voting_controller.vote(three_reapers_stub[1], farm_token, 20, {'from': neo})
    voting_controller.vote(three_reapers_stub[2], farm_token, 30, {'from': neo})
    voting_controller.vote(three_reapers_stub[2], farm_token, 40, {'from': neo})
    assert farm_token.balanceOf(neo) == initial_balance - 100
    assert farm_token.balanceOf(voting_controller) == 100

    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 7 * 10 ** 17
    assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 10
    assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 20
    assert voting_controller.accountVotePower(three_reapers_stub[2], neo) == 70

    voting_controller.vote(three_reapers_stub[0], farm_token, 10, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[1], farm_token, 20, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[2], farm_token, 30, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[2], farm_token, 40, {'from': morpheus})

    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 7 * 10 ** 17
    assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 10
    assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 20
    assert voting_controller.accountVotePower(three_reapers_stub[2], neo) == 70
    assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 10
    assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 20
    assert voting_controller.accountVotePower(three_reapers_stub[2], morpheus) == 70

    voting_controller.snapshot()
    brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

    assert voting_controller.reaperIntegratedVotes(three_reapers_stub[0]) == 0
    assert voting_controller.reaperIntegratedVotes(three_reapers_stub[1]) == 0
    assert voting_controller.reaperIntegratedVotes(three_reapers_stub[2]) == 0
    assert voting_controller.lastVotes(three_reapers_stub[0]) == 333333333333333333
    assert voting_controller.lastVotes(three_reapers_stub[1]) == 333333333333333333
    assert voting_controller.lastVotes(three_reapers_stub[2]) == 333333333333333333
    
    voting_controller.snapshot()
    brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

    assert voting_controller.reaperBalances(three_reapers_stub[0], farm_token) == 20
    assert voting_controller.reaperBalances(three_reapers_stub[1], farm_token) == 40
    assert voting_controller.reaperBalances(three_reapers_stub[2], farm_token) == 140
    assert voting_controller.reaperIntegratedVotes(three_reapers_stub[0]) == 333333333333333333 * WEEK
    assert voting_controller.reaperIntegratedVotes(three_reapers_stub[1]) == 333333333333333333 * WEEK
    assert voting_controller.reaperIntegratedVotes(three_reapers_stub[2]) == 333333333333333333 * WEEK
    assert voting_controller.lastVotes(three_reapers_stub[0]) == 1 * 10 ** 17
    assert voting_controller.lastVotes(three_reapers_stub[1]) == 2 * 10 ** 17
    assert voting_controller.lastVotes(three_reapers_stub[2]) == 7 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 7 * 10 ** 17

    voting_controller.vote(three_reapers_stub[0], farm_token, 30, {'from': neo})
    voting_controller.vote(three_reapers_stub[1], farm_token, 10, {'from': neo})
    voting_controller.vote(three_reapers_stub[2], farm_token, 60, {'from': neo})

    assert voting_controller.reaperBalances(three_reapers_stub[0], farm_token) == 50
    assert voting_controller.reaperBalances(three_reapers_stub[1], farm_token) == 50
    assert voting_controller.reaperBalances(three_reapers_stub[2], farm_token) == 200
    assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 40
    assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 30
    assert voting_controller.accountVotePower(three_reapers_stub[2], neo) == 130
    assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 10
    assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 20
    assert voting_controller.accountVotePower(three_reapers_stub[2], morpheus) == 70
    
    voting_controller.vote(three_reapers_stub[0], farm_token, 50, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[1], farm_token, 50, {'from': morpheus})
    assert voting_controller.reaperBalances(three_reapers_stub[0], farm_token) == 100
    assert voting_controller.reaperBalances(three_reapers_stub[1], farm_token) == 100
    assert voting_controller.reaperBalances(three_reapers_stub[2], farm_token) == 200
    assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 40
    assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 30
    assert voting_controller.accountVotePower(three_reapers_stub[2], neo) == 130
    assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 60
    assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 70
    assert voting_controller.accountVotePower(three_reapers_stub[2], morpheus) == 70

    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 2.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 5 * 10 ** 17

    voting_controller.vote(three_reapers_stub[0], farm_token, 1000, {'from': morpheus})
    assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 1060
    assert 7.8 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[0]) <= 7.9 * 10 ** 17
    assert 0.7 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[1]) <= 0.8 * 10 ** 17
    assert 1.4 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[2]) <= 1.5 * 10 ** 17
    assert 10 ** 18 - 1 <= voting_controller.reaperVotePower(three_reapers_stub[0]) + voting_controller.reaperVotePower(three_reapers_stub[1]) + voting_controller.reaperVotePower(three_reapers_stub[2]) <= 10 ** 18

    with brownie.reverts("tokens are locked"):
        voting_controller.unvote(three_reapers_stub[0], farm_token, 1000, {'from': morpheus})

    brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

    voting_controller.unvote(three_reapers_stub[0], farm_token, 1000, {'from': morpheus})
    assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 60
    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 2.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 5 * 10 ** 17

    assert voting_controller.lastVotes(three_reapers_stub[0]) == 1 * 10 ** 17
    assert voting_controller.lastVotes(three_reapers_stub[1]) == 2 * 10 ** 17
    assert voting_controller.lastVotes(three_reapers_stub[2]) == 7 * 10 ** 17
    
    voting_controller.snapshot()

    assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 2.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.reaperVotePower(three_reapers_stub[2]) == 5 * 10 ** 17

    assert voting_controller.lastVotes(three_reapers_stub[0]) == 2.5 * 10 ** 17
    assert voting_controller.lastVotes(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.lastVotes(three_reapers_stub[2]) == 5 * 10 ** 17
