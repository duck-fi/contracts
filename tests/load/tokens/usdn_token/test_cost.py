import brownie
import pytest
from brownie.test import given, strategy


def test_cost_deposit(usdn_token, accounts):  
    for i in range(0, 100):
        usdn_token.deposit(accounts[2], 1)


def test_cost_stake(usdn_token, accounts):  
    for i in range(0, 100):
        usdn_token.stake(1)
    


def test_cost_transfer(usdn_token, accounts):  
    for i in range(0, 100):
        usdn_token.transfer(accounts[0], 1, {'from': accounts[2]})
