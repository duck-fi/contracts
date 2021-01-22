import brownie
import pytest
from brownie.test import given, strategy


def test_complex_v1(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 100)
    usdn_token.deposit(accounts[1], 100)
    usdn_token.stake(20)

    assert usdn_token.balanceOf(accounts[0]) == 100
    assert usdn_token.balanceOf(accounts[1]) == 100
    assert usdn_token.totalSupply() == 200

    usdn_token.transfer(accounts[1], 100)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 200
    assert usdn_token.totalSupply() == 200

    usdn_token.stake(80)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 280
    assert usdn_token.totalSupply() == 280

    usdn_token.transfer(accounts[0], 140, {'from': accounts[1]})
    assert usdn_token.balanceOf(accounts[0]) == 140
    assert usdn_token.balanceOf(accounts[1]) == 140
    assert usdn_token.totalSupply() == 280

    usdn_token.deposit(accounts[2], 140)
    usdn_token.transfer(accounts[1], 140)
    usdn_token.stake(140)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 420
    assert usdn_token.balanceOf(accounts[2]) == 140
    assert usdn_token.totalSupply() == 560
