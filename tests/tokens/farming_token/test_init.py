#!/usr/bin/python3
# pylint: disable=no-value-for-parameter

from brownie.test import given, strategy


def test_init_token(farming_token, deployer, morpheus, trinity, oracle):
    assert farming_token.name() == "Test Token"
    assert farming_token.symbol() == "TST"
    assert farming_token.decimals() == 18

    assert farming_token.totalSupply() == 100000*10**18
    assert farming_token.balanceOf(deployer) == farming_token.totalSupply()
    assert farming_token.balanceOf(morpheus) == 0
    assert farming_token.balanceOf(trinity) == 0
    assert farming_token.balanceOf(oracle) == 0


def test_initial_balances(farming_token, deployer):
    @given(account=strategy('address', exclude=deployer))
    def test_balance_is_zero(account):
        assert farming_token.balanceOf(account) == 0
    test_balance_is_zero()
