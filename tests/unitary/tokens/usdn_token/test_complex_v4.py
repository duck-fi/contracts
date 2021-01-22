import brownie
import pytest
from brownie.test import given, strategy


def test_complex_v4(usdn_token, accounts):
    usdn_token.deposit(accounts[1], 1)
    usdn_token.deposit(accounts[0], 1000100)
    usdn_token.stake(100)
    assert usdn_token.balanceOf(accounts[0]) == 1000100
    assert usdn_token.balanceOf(accounts[1]) == 1
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 1000101

    usdn_token.deposit(accounts[1], 99)
    usdn_token.deposit(accounts[2], 25)
    usdn_token.deposit(accounts[3], 4000000)
    usdn_token.withdraw(accounts[0])
    usdn_token.deposit(accounts[1], 4900)
    usdn_token.deposit(accounts[2], 9975)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 5000
    assert usdn_token.balanceOf(accounts[2]) == 10000
    assert usdn_token.balanceOf(accounts[3]) == 4000000
    assert usdn_token.totalSupply() == 4015000

    usdn_token.stake(100000)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 105000
    assert usdn_token.balanceOf(accounts[2]) == 10000
    assert usdn_token.balanceOf(accounts[3]) == 4000000
    assert usdn_token.totalSupply() == 4115000
