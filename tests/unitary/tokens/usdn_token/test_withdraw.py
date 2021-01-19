import brownie
import pytest
from brownie.test import given, strategy


def test_withdraw_not_owner(usdn_token, accounts):
    with brownie.reverts("Ownable: caller is not the owner or admin"):
        usdn_token.withdraw(accounts[1], {'from': accounts[1]})


def test_withdraw(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 1)

    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.totalSupply() == 1

    usdn_token.withdraw(accounts[0])

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.totalSupply() == 0


def test_withdraw_after_deposit(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 2)

    assert usdn_token.balanceOf(accounts[0]) == 2
    assert usdn_token.totalSupply() == 2

    usdn_token.withdraw(accounts[0])

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.totalSupply() == 0


def test_withdraw_after_staking_reward(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 1)
    usdn_token.stake(1)
    usdn_token.withdraw(accounts[0])

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.totalSupply() == 0


def test_withdraw_complex(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 2)
    assert usdn_token.balanceOf(accounts[0]) == 2

    usdn_token.stake(2)
    assert usdn_token.balanceOf(accounts[0]) == 2

    usdn_token.withdraw(accounts[0])
    assert usdn_token.totalSupply() == 0
    assert usdn_token.balanceOf(accounts[0]) == 0
