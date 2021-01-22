#!/usr/bin/python3

import brownie
from brownie.test import given, strategy

# TODO: rewrite these tests (transfer, transferFrom) via StateMachine (https://eth-brownie.readthedocs.io/en/stable/tests-hypothesis-stateful.html)

@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_transfer(farm_token, neo, morpheus, amount):
    total_supply = farm_token.totalSupply()
    sender_balance = farm_token.balanceOf(neo)
    receiver_balance = farm_token.balanceOf(morpheus)

    tx = farm_token.transfer(morpheus, amount, {'from': neo})
    assert tx.return_value is True
    assert farm_token.balanceOf(morpheus) == receiver_balance + amount
    assert farm_token.balanceOf(neo) == sender_balance - amount
    assert farm_token.totalSupply() == total_supply


def test_transfer_full_balance(farm_token, neo, morpheus):
    amount = farm_token.balanceOf(neo)
    receiver_balance = farm_token.balanceOf(morpheus)

    farm_token.transfer(morpheus, amount, {'from': neo})

    assert farm_token.balanceOf(neo) == 0
    assert farm_token.balanceOf(morpheus) == receiver_balance + amount


def test_transfer_zero_tokens(farm_token, neo, morpheus):
    sender_balance = farm_token.balanceOf(neo)
    receiver_balance = farm_token.balanceOf(morpheus)

    farm_token.transfer(morpheus, 0, {'from': neo})

    assert farm_token.balanceOf(neo) == sender_balance
    assert farm_token.balanceOf(morpheus) == receiver_balance


def test_transfer_to_self(farm_token, neo, morpheus):
    sender_balance = farm_token.balanceOf(neo)
    amount = sender_balance

    farm_token.transfer(neo, amount, {'from': neo})

    assert farm_token.balanceOf(neo) == sender_balance


def test_insufficient_balance(farm_token, neo, morpheus):
    balance = farm_token.balanceOf(neo)

    with brownie.reverts():
        farm_token.transfer(
            morpheus, balance + 1, {'from': neo})


def test_transfer_event_fires(farm_token, neo, morpheus):
    amount = farm_token.balanceOf(neo)
    tx = farm_token.transfer(morpheus, amount, {'from': neo})

    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [neo, morpheus, amount]
