import brownie
import pytest
from brownie.test import given, strategy


def test_deprecate(usdn_token, accounts):
    usdn_token.deprecate()

    with brownie.reverts("Deprecateble: contract is deprecated"):
        usdn_token.deposit(accounts[0], 1)

    with brownie.reverts("Deprecateble: contract is deprecated"):
        usdn_token.stake(1)

    with brownie.reverts("Deprecateble: contract is deprecated"):
        usdn_token.withdraw(accounts[0])

    with brownie.reverts("Deprecateble: contract is deprecated"):
        usdn_token.transfer(accounts[1], 2)

    with brownie.reverts("Deprecateble: contract is deprecated"):
        usdn_token.transferFrom(accounts[1], accounts[1], 2)

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.totalSupply() == 0
