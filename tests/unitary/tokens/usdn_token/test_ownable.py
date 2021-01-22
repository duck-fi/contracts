import brownie
import pytest
from brownie.test import given, strategy


def test_ownable_not_owner(usdn_token, accounts):
    with brownie.reverts("Ownable: caller is not the owner or admin"):
        usdn_token.deposit(accounts[0], 1, {'from': accounts[1]})


def test_ownable_transfer_ownership(usdn_token, accounts):
    usdn_token.transferOwnership(accounts[1])
    usdn_token.deposit(accounts[0], 1)

    assert usdn_token.totalSupply() == 1
    assert usdn_token.balanceOf(accounts[0]) == 1
    assert usdn_token.balanceOf(accounts[1]) == 0
