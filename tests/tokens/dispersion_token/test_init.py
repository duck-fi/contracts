#!/usr/bin/python3


from brownie import accounts
from brownie.test import given, strategy


def test_init(token, neo, morpheus, trinity, oracle):
    assert token.name() == "Test Token"
    assert token.symbol() == "TST"
    assert token.decimals() == 18
    assert token.totalSupply() == 100000*10**18
    assert token.balanceOf(neo) == token.totalSupply()


@given(account=strategy('address', exclude=accounts[0]))
def test_initial_supply(token, account):
    assert token.balanceOf(account) == 0
