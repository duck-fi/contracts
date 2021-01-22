import brownie
import pytest
from brownie.test import given, strategy


def test_365(usdn_token, accounts):    
    MUL: constant(uint256) = 10 ** 18
    USDN_MAX: constant(uint256) = 10 ** 12

    usdn_token.deposit(accounts[0], 2*USDN_MAX*MUL)
    usdn_token.transfer(accounts[1], 1*USDN_MAX*MUL)
    usdn_token.transfer(accounts[1], 1*USDN_MAX*MUL)
    usdn_token.transfer(accounts[0], 1*USDN_MAX*MUL, {'from': accounts[1]})

    for i in range(0, 365):
        totalSupply: uint256 = usdn_token.totalSupply() / 365
        usdn_token.stake(totalSupply)
    
    assert usdn_token.balanceOf(accounts[0]) == 2707150630289000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2707150630289000000000000000000
    assert usdn_token.totalSupply() == 5414301261956197403000000000000

    for i in range(0, 365):
        totalSupply: uint256 = usdn_token.totalSupply() / 365
        usdn_token.stake(totalSupply)
    

    assert usdn_token.balanceOf(accounts[0]) == 7348743068538000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 7348743068538000000000000000000
    assert usdn_token.totalSupply() == 14697486143576291307000000000000
