import brownie
import pytest
from brownie.test import given, strategy


def test_staking_ownership(usdn_token, accounts):
    with brownie.reverts("Ownable: caller is not the owner or admin"):
        usdn_token.stake(1, {'from': accounts[1]})



def test_staking_equal_amounts(usdn_token, accounts):
    assert usdn_token.totalSupply() == 0

    usdn_token.deposit(accounts[0], 10 ** 12)
    usdn_token.deposit(accounts[1], 10 ** 12)
    usdn_token.deposit(accounts[2], 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)

    assert usdn_token.totalSupply() == 3000000000000
    assert usdn_token.balanceOf(accounts[0]) == 1000000000000
    assert usdn_token.balanceOf(accounts[1]) == 1000000000000
    assert usdn_token.balanceOf(accounts[2]) == 1000000000000


def test_staking_many(usdn_token, accounts):
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)

    assert usdn_token.totalSupply() == 33000000000000
    assert usdn_token.balanceOf(accounts[0]) == 10999999999982
    assert usdn_token.balanceOf(accounts[1]) == 10999999999982
    assert usdn_token.balanceOf(accounts[2]) == 10999999999982


def test_staking(usdn_token, accounts):
    usdn_token.deposit(accounts[3], 26 * 10 ** 12)

    assert usdn_token.totalSupply() == 59000000000000
    assert usdn_token.balanceOf(accounts[0]) == 10999999999982
    assert usdn_token.balanceOf(accounts[1]) == 10999999999982
    assert usdn_token.balanceOf(accounts[2]) == 10999999999982
    assert usdn_token.balanceOf(accounts[3]) == 26000000000000

    usdn_token.stake(6 * 10 ** 12)

    assert usdn_token.totalSupply() == 65000000000000
    assert usdn_token.balanceOf(accounts[0]) == 12999999999976
    assert usdn_token.balanceOf(accounts[1]) == 12999999999976
    assert usdn_token.balanceOf(accounts[2]) == 12999999999976
    assert usdn_token.balanceOf(accounts[3]) == 26000000000000


def test_staking_huge_reward(usdn_token, accounts):
    usdn_token.stake(6000 * 10 ** 12)
    assert usdn_token.totalSupply() == 6065000000000000
    assert usdn_token.balanceOf(accounts[0]) == 1212999999997756
    assert usdn_token.balanceOf(accounts[1]) == 1212999999997756
    assert usdn_token.balanceOf(accounts[2]) == 1212999999997756
    assert usdn_token.balanceOf(accounts[3]) == 2425999999999990
