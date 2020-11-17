#!/usr/bin/python3

import brownie
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_sender_balance_decreases(farming_token, neo, morpheus, trinity, amount):
    sender_balance = farming_token.balanceOf(neo)
    receiver_balance = farming_token.balanceOf(trinity)
    caller_balance = farming_token.balanceOf(morpheus)
    total_supply = farming_token.totalSupply()

    farming_token.approve(morpheus, sender_balance, {'from': neo})
    farming_token.approve(trinity, sender_balance, {'from': neo})
    tx = farming_token.transferFrom(neo, trinity, amount, {'from': morpheus})
    assert tx.return_value is True
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [neo, trinity, amount]

    assert farming_token.balanceOf(neo) == sender_balance - amount
    assert farming_token.balanceOf(trinity) == receiver_balance + amount
    assert farming_token.balanceOf(morpheus) == caller_balance
    assert farming_token.totalSupply() == total_supply
    assert farming_token.allowance(neo, morpheus) == sender_balance - amount
    assert farming_token.allowance(neo, trinity) == sender_balance


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_max_allowance(farming_token, neo, morpheus, trinity, amount):
    farming_token.approve(morpheus, 0, {'from': neo})
    farming_token.approve(morpheus, 2**256 - 1, {'from': neo})
    farming_token.transferFrom(neo, trinity, amount, {'from': morpheus})

    assert farming_token.allowance(neo, morpheus) == 2**256 - 1


def test_transfer_zero_tokens(farming_token, neo, morpheus, trinity):
    sender_balance = farming_token.balanceOf(neo)
    receiver_balance = farming_token.balanceOf(morpheus)

    farming_token.approve(morpheus, 0, {'from': neo})
    farming_token.approve(morpheus, 10, {'from': neo})
    farming_token.transferFrom(neo, trinity, 0, {'from': morpheus})

    assert farming_token.balanceOf(neo) == sender_balance
    assert farming_token.balanceOf(morpheus) == receiver_balance


def test_no_approval(farming_token, neo, morpheus, trinity, oracle):
    balance = farming_token.balanceOf(neo)
    with brownie.reverts():
        farming_token.transferFrom(
            trinity, oracle, balance, {'from': morpheus})


def test_revoked_approval(farming_token, neo, morpheus, trinity):
    balance = farming_token.balanceOf(neo)
    farming_token.approve(morpheus, 0, {'from': neo})

    with brownie.reverts():
        farming_token.transferFrom(neo, trinity, balance, {'from': morpheus})


def test_insufficient_approval(farming_token, neo, morpheus, trinity):
    balance = farming_token.balanceOf(neo)

    farming_token.approve(morpheus, balance - 1, {'from': neo})
    with brownie.reverts():
        farming_token.transferFrom(neo, trinity, balance, {'from': morpheus})


def test_transfer_to_self_no_approval(farming_token, neo):
    amount = farming_token.balanceOf(neo)

    with brownie.reverts():
        farming_token.transferFrom(neo, neo, amount, {'from': neo})


def test_transfer_to_self(farming_token, neo):
    sender_balance = farming_token.balanceOf(neo)
    amount = sender_balance

    farming_token.approve(neo, sender_balance, {'from': neo})
    farming_token.transferFrom(neo, neo, amount, {'from': neo})

    assert farming_token.balanceOf(neo) == sender_balance
    assert farming_token.allowance(neo, neo) == sender_balance - amount


def test_insufficient_balance(farming_token, neo, morpheus, trinity):
    balance = farming_token.balanceOf(morpheus)

    farming_token.approve(neo, balance + 1, {'from': morpheus})
    with brownie.reverts():
        farming_token.transferFrom(
            morpheus, trinity, balance + 1, {'from': neo})


def test_transfer_zero_tokens_without_approval(farming_token, neo, morpheus, trinity):
    sender_balance = farming_token.balanceOf(morpheus)
    receiver_balance = farming_token.balanceOf(trinity)

    farming_token.transferFrom(morpheus, trinity, 0, {'from': neo})

    assert farming_token.balanceOf(morpheus) == sender_balance
    assert farming_token.balanceOf(trinity) == receiver_balance


def test_transfer_full_balance(farming_token, neo, morpheus, trinity):
    amount = farming_token.balanceOf(morpheus)
    receiver_balance = farming_token.balanceOf(trinity)

    farming_token.approve(neo, amount, {'from': morpheus})
    farming_token.transferFrom(morpheus, trinity, amount, {'from': neo})

    assert farming_token.balanceOf(morpheus) == 0
    assert farming_token.balanceOf(trinity) == receiver_balance + amount


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_approve_supply_controller(farming_token, neo, oracle, amount, supply_controller):
    sender_balance = farming_token.balanceOf(neo)
    receiver_balance = farming_token.balanceOf(oracle)
    caller_balance = farming_token.balanceOf(supply_controller)
    total_supply = farming_token.totalSupply()

    farming_token.approve(neo, 0, {'from': oracle})
    farming_token.approve(oracle, 0, {'from': neo})
    farming_token.transferFrom(
        neo, oracle, amount, {'from': supply_controller})

    assert farming_token.balanceOf(neo) == sender_balance - amount
    assert farming_token.balanceOf(oracle) == receiver_balance + amount
    assert farming_token.balanceOf(supply_controller) == caller_balance
    assert farming_token.totalSupply() == total_supply
