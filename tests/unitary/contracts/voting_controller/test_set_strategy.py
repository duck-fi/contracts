#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


def test_set_strategy(voting_controller, farm_token, voting_strategy_stub, ZERO_ADDRESS, neo, morpheus):
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS

    with brownie.reverts("unauthorized"):
        voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': morpheus})

    voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': neo})
    assert voting_controller.strategies(farm_token) == voting_strategy_stub
    assert voting_controller.coins(farm_token)

    voting_controller.setStrategy(farm_token, ZERO_ADDRESS, {'from': neo})
    assert voting_controller.strategies(farm_token) == ZERO_ADDRESS
    assert not voting_controller.coins(farm_token)
