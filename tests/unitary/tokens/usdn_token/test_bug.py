import brownie
import pytest
from brownie.test import given, strategy


def getSumBalances(usdn_token, accounts) -> int:
    temp: uint256 = 0

    for i in range(0,10):
        temp += usdn_token.balanceOf(accounts[i])

    return temp


def test_bug(usdn_token, accounts):  
    usdn_token.deposit(accounts[1], 10000000000000000000)                           # 10678639
    usdn_token.deposit(accounts[2], 99999999000000000000)                           # 10678724
    usdn_token.transfer(accounts[3], 10000000000000000000, {'from': accounts[1]})   # 10678728
    usdn_token.withdraw(accounts[3])                                                # 10678740
    usdn_token.deposit(accounts[4], 99999999000000000000)                           # 10678751
    usdn_token.withdraw(accounts[4])                                                # 10678761
    usdn_token.deposit(accounts[1], 10002323000000000000)                           # 10678835
    usdn_token.deposit(accounts[5], 5000000000000000000)                            # 10678882
    usdn_token.deposit(accounts[3], 10002323000000000000)                           # 10678890
    usdn_token.withdraw(accounts[3])                                                # 10678901

    assert getSumBalances(usdn_token, accounts) == usdn_token.totalSupply()

    usdn_token.deposit(accounts[2], 99999999000000000000)                           # 10678913
    usdn_token.transfer(accounts[4], 99999999000000000000, {'from': accounts[2]})   # 10678941
    usdn_token.withdraw(accounts[4])                                                # 10678956
    usdn_token.deposit(accounts[2], 50000000000000000000)                           # 10679019
    usdn_token.deposit(accounts[2], 50000000000000000000)                           # 10679197
    usdn_token.deposit(accounts[6], 990257175000000000000)                          # 10679342
    usdn_token.deposit(accounts[7], 1000000000000000000000)                         # 10683151
    usdn_token.transfer(accounts[8], 50000000000000000000, {'from': accounts[7]})   # 10683658
    usdn_token.approve(accounts[9], 115792089237316195423570985008687907853269984665640564039457584007913129639935, {'from': accounts[7]}) # 10683852
    usdn_token.stake(672876000000000000)
    
    assert getSumBalances(usdn_token, accounts) == usdn_token.totalSupply()
