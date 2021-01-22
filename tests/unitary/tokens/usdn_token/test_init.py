import brownie
import pytest
from brownie.test import given, strategy


def test_init(usdn_token, accounts):
    assert usdn_token.name() == "Neutrino USD"
    assert usdn_token.symbol() == "USDN"
    assert usdn_token.decimals() == 18

    assert usdn_token.totalSupply() == 0
    assert usdn_token.balanceOf(accounts[0]) == 0
