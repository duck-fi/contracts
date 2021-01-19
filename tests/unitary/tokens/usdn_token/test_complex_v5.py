import brownie
import pytest
from brownie.test import given, strategy


def test_complex_v5(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 100)
    usdn_token.withdraw(accounts[0])
    usdn_token.deposit(accounts[0], 1000)
    usdn_token.deposit(accounts[1], 1000)
    assert usdn_token.balanceOf(accounts[0]) == 1000
    assert usdn_token.balanceOf(accounts[1]) == 1000
    assert usdn_token.totalSupply() == 2000

    usdn_token.stake(100)
    assert usdn_token.balanceOf(accounts[0]) == 1000
    assert usdn_token.balanceOf(accounts[1]) == 1000
    assert usdn_token.totalSupply() == 2000

    usdn_token.deposit(accounts[2], 1000)
    usdn_token.stake(100)
    assert usdn_token.balanceOf(accounts[0]) == 1050
    assert usdn_token.balanceOf(accounts[1]) == 1050
    assert usdn_token.balanceOf(accounts[2]) == 1000
    assert usdn_token.totalSupply() == 3100

    usdn_token.withdraw(accounts[2])
    usdn_token.stake(100)
    assert usdn_token.balanceOf(accounts[0]) == 1099
    assert usdn_token.balanceOf(accounts[1]) == 1099
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 2200
