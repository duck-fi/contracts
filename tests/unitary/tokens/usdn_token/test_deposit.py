import brownie
import pytest
from brownie.test import given, strategy


def test_deposit_not_owner(usdn_token, accounts):
    with brownie.reverts("Ownable: caller is not the owner or admin"):
        usdn_token.deposit(accounts[0], 1, {'from': accounts[1]})


def test_deposit_zero(usdn_token, accounts):
    with brownie.reverts("amount should be > 0"):
        usdn_token.deposit(accounts[3], 0)


def test_deposit(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 1)
    usdn_token.deposit(accounts[1], 2)

    assert usdn_token.totalSupply() == 3
    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.balanceOf(accounts[1]) == 2


def test_deposit_many(usdn_token, accounts):
    usdn_token.deposit(accounts[2], 1)
    usdn_token.deposit(accounts[2], 2)
    usdn_token.deposit(accounts[2], 3)

    assert usdn_token.totalSupply() == 9
    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.balanceOf(accounts[1]) == 2
    assert usdn_token.balanceOf(accounts[2]) == 6
