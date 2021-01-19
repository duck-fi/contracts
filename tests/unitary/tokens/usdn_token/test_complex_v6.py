import brownie
import pytest
from brownie.test import given, strategy


def test_complex_v6(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 100)
    usdn_token.deposit(accounts[1], 100)
    usdn_token.stake(2)
    usdn_token.transfer(accounts[2], 100)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 100
    assert usdn_token.balanceOf(accounts[2]) == 100
    assert usdn_token.totalSupply() == 200

    usdn_token.stake(2)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 101
    assert usdn_token.balanceOf(accounts[2]) == 101
    assert usdn_token.totalSupply() == 202

    usdn_token.transfer(accounts[1], 101, {'from': accounts[2]})
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 202
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 202

    usdn_token.stake(2)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 203
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 204

    usdn_token.transfer(accounts[0], 101, {'from': accounts[1]})
    usdn_token.transfer(accounts[2], 101, {'from': accounts[1]})
    usdn_token.deposit(accounts[1], 101)
    usdn_token.stake(3)
    assert usdn_token.balanceOf(accounts[0]) == 102
    assert usdn_token.balanceOf(accounts[1]) == 102
    assert usdn_token.balanceOf(accounts[2]) == 102
    assert usdn_token.totalSupply() == 308

    usdn_token.transfer(accounts[0], 102, {'from': accounts[1]})
    usdn_token.withdraw(accounts[0])
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 0
    assert usdn_token.balanceOf(accounts[2]) == 102
    assert usdn_token.totalSupply() == 104

    usdn_token.deposit(accounts[1], 210)
    usdn_token.stake(3)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 210
    assert usdn_token.balanceOf(accounts[2]) == 105
    assert usdn_token.totalSupply() == 317

    usdn_token.transfer(accounts[0], 104, {'from': accounts[2]})
    usdn_token.deposit(accounts[1], 210)
    usdn_token.deposit(accounts[2], 210)
    usdn_token.stake(1)
    assert usdn_token.balanceOf(accounts[0]) == 104
    assert usdn_token.balanceOf(accounts[1]) == 420
    assert usdn_token.balanceOf(accounts[2]) == 211
    assert usdn_token.totalSupply() == 738
