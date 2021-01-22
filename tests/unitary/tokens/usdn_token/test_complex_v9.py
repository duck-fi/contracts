import brownie
import pytest
from brownie.test import given, strategy


def test_complex_v9(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 2)
    usdn_token.deposit(accounts[1], 2)
    usdn_token.stake(1)
    assert usdn_token.balanceOf(accounts[0]) == 2
    assert usdn_token.balanceOf(accounts[1]) == 2
    assert usdn_token.totalSupply() == 4

    usdn_token.transfer(accounts[1], 1)
    usdn_token.deposit(accounts[0], 1)
    usdn_token.transfer(accounts[1], 2)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 5
    assert usdn_token.totalSupply() == 5

    usdn_token.stake(1)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 6
    assert usdn_token.totalSupply() == 6
