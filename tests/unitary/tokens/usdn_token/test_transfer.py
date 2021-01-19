import brownie
import pytest
from brownie.test import given, strategy


def test_transfer_zero_amount(usdn_token, accounts):
    with brownie.reverts("amount should be > 0"):
        usdn_token.transfer(accounts[1], 0)


def test_transfer_huge_amount(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 1)

    with brownie.reverts("ERC20: transfer amount exceeds balance"):
        usdn_token.transfer(accounts[1], 2)


def test_transfer(usdn_token, accounts):
    usdn_token.transfer(accounts[1], 1)

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 1
    assert usdn_token.totalSupply() == 1


def test_transfer_after_deposit(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 2)

    assert usdn_token.balanceOf(accounts[0]) == 2
    assert usdn_token.balanceOf(accounts[1]) == 1

    usdn_token.transfer(accounts[1], 2)

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 3
    assert usdn_token.totalSupply() == 3


def test_transfer_after_staking_reward(usdn_token, accounts):
    usdn_token.stake(1)

    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 3
    assert usdn_token.totalSupply() == 3

    usdn_token.transfer(accounts[0], 3, {'from': accounts[1]})

    assert usdn_token.balanceOf(accounts[0]) == 3
    assert usdn_token.balanceOf(accounts[1]) == 0
    assert usdn_token.totalSupply() == 3


def test_transfer_before_staking_reward(usdn_token, accounts):
    usdn_token.transfer(accounts[1], 2)

    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.balanceOf(accounts[1]) == 2
    assert usdn_token.balanceOf(accounts[2]) == 0

    usdn_token.stake(2)

    assert usdn_token.totalSupply() == 5
    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.balanceOf(accounts[1]) == 3


def test_transferFrom(usdn_token, accounts):
    usdn_token.approve(accounts[1], 1)

    assert usdn_token.allowance(accounts[0], accounts[1]) == 1

    usdn_token.transferFrom(accounts[0], accounts[1], 1, {'from': accounts[1]})

    assert usdn_token.totalSupply() == 5
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 4
    assert usdn_token.balanceOf(accounts[2]) == 0


def test_transferFrom_allowance(usdn_token, accounts):
    usdn_token.increaseAllowance(accounts[0], 1, {'from': accounts[1]})

    assert usdn_token.allowance(accounts[1], accounts[0]) == 1

    usdn_token.transferFrom(accounts[1], accounts[0], 1)

    assert usdn_token.totalSupply() == 5
    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.balanceOf(accounts[1]) == 3

    usdn_token.increaseAllowance(accounts[0], 1, {'from': accounts[1]})
    assert usdn_token.allowance(accounts[1], accounts[0]) == 1

    usdn_token.decreaseAllowance(accounts[0], 1, {'from': accounts[1]})
    assert usdn_token.allowance(accounts[1], accounts[0]) == 0
