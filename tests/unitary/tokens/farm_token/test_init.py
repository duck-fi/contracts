#!/usr/bin/python3
# pylint: disable=no-value-for-parameter

import pytest
import brownie
from brownie.test import given, strategy


def test_init_token(farm_token, deployer, morpheus, trinity, oracle):
    assert farm_token.name() == "Dispersion Farm Token"
    assert farm_token.symbol() == "DFT"
    assert farm_token.decimals() == 18

    assert farm_token.totalSupply() == 100000*10**18
    assert farm_token.balanceOf(deployer) == farm_token.totalSupply()
    assert farm_token.balanceOf(morpheus) == 0
    assert farm_token.balanceOf(trinity) == 0
    assert farm_token.balanceOf(oracle) == 0


def test_initial_balances(farm_token, deployer):
    @given(account=strategy('address', exclude=deployer))
    def test_balance_is_zero(account):
        assert farm_token.balanceOf(account) == 0
    test_balance_is_zero()
