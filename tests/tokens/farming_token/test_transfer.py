#!/usr/bin/python3

import brownie
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_transfer(farming_token, neo, morpheus, amount):
    total_supply = farming_token.totalSupply()
    sender_balance = farming_token.balanceOf(neo)
    receiver_balance = farming_token.balanceOf(morpheus)

    tx = farming_token.transfer(morpheus, amount, {'from': neo})
    assert tx.return_value is True
    assert farming_token.balanceOf(morpheus) == receiver_balance + amount
    assert farming_token.balanceOf(neo) == sender_balance - amount
    assert farming_token.totalSupply() == total_supply


def test_transfer_full_balance(farming_token, neo, morpheus):
    amount = farming_token.balanceOf(neo)
    receiver_balance = farming_token.balanceOf(morpheus)

    farming_token.transfer(morpheus, amount, {'from': neo})

    assert farming_token.balanceOf(neo) == 0
    assert farming_token.balanceOf(morpheus) == receiver_balance + amount


def test_transfer_zero_tokens(farming_token, neo, morpheus):
    sender_balance = farming_token.balanceOf(neo)
    receiver_balance = farming_token.balanceOf(morpheus)

    farming_token.transfer(morpheus, 0, {'from': neo})

    assert farming_token.balanceOf(neo) == sender_balance
    assert farming_token.balanceOf(morpheus) == receiver_balance


def test_transfer_to_self(farming_token, neo, morpheus):
    sender_balance = farming_token.balanceOf(neo)
    amount = sender_balance

    farming_token.transfer(neo, amount, {'from': neo})

    assert farming_token.balanceOf(neo) == sender_balance


def test_insufficient_balance(farming_token, neo, morpheus):
    balance = farming_token.balanceOf(neo)

    with brownie.reverts():
        farming_token.transfer(
            morpheus, balance + 1, {'from': neo})


def test_transfer_event_fires(farming_token, neo, morpheus):
    amount = farming_token.balanceOf(neo)
    tx = farming_token.transfer(morpheus, amount, {'from': neo})

    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [neo, morpheus, amount]
