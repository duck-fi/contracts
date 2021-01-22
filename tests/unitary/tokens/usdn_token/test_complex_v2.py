import brownie
import pytest
from brownie.test import given, strategy


def test_complex_v2(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 100)
    usdn_token.stake(20)
    assert usdn_token.balanceOf(accounts[0]) == 100

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 99
    assert usdn_token.balanceOf(accounts[1]) == 11
    assert usdn_token.totalSupply() == 110

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 97
    assert usdn_token.balanceOf(accounts[1]) == 22
    assert usdn_token.totalSupply() == 120

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 94
    assert usdn_token.balanceOf(accounts[1]) == 34
    assert usdn_token.totalSupply() == 130

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 90
    assert usdn_token.balanceOf(accounts[1]) == 47
    assert usdn_token.totalSupply() == 140

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 85
    assert usdn_token.balanceOf(accounts[1]) == 61
    assert usdn_token.totalSupply() == 150

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 79
    assert usdn_token.balanceOf(accounts[1]) == 75
    assert usdn_token.totalSupply() == 160

    usdn_token.transfer(accounts[1], 10)
    usdn_token.stake(10)
    assert usdn_token.balanceOf(accounts[0]) == 73
    assert usdn_token.balanceOf(accounts[1]) == 90
    assert usdn_token.totalSupply() == 170
