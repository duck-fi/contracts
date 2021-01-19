#!/usr/bin/python3

import brownie
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_sender_balance_decreases(farm_token, neo, morpheus, trinity, amount):
    sender_balance = farm_token.balanceOf(neo)
    receiver_balance = farm_token.balanceOf(trinity)
    caller_balance = farm_token.balanceOf(morpheus)
    total_supply = farm_token.totalSupply()

    farm_token.approve(morpheus, sender_balance, {'from': neo})
    farm_token.approve(trinity, sender_balance, {'from': neo})
    tx = farm_token.transferFrom(neo, trinity, amount, {'from': morpheus})
    assert tx.return_value is True
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [neo, trinity, amount]

    assert farm_token.balanceOf(neo) == sender_balance - amount
    assert farm_token.balanceOf(trinity) == receiver_balance + amount
    assert farm_token.balanceOf(morpheus) == caller_balance
    assert farm_token.totalSupply() == total_supply
    assert farm_token.allowance(neo, morpheus) == sender_balance - amount
    assert farm_token.allowance(neo, trinity) == sender_balance


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_max_allowance(farm_token, neo, morpheus, trinity, amount):
    farm_token.approve(morpheus, 0, {'from': neo})
    farm_token.approve(morpheus, 2**256 - 1, {'from': neo})
    farm_token.transferFrom(neo, trinity, amount, {'from': morpheus})

    assert farm_token.allowance(neo, morpheus) == 2**256 - 1


def test_transfer_zero_tokens(farm_token, neo, morpheus, trinity):
    sender_balance = farm_token.balanceOf(neo)
    receiver_balance = farm_token.balanceOf(morpheus)

    farm_token.approve(morpheus, 0, {'from': neo})
    farm_token.approve(morpheus, 10, {'from': neo})
    farm_token.transferFrom(neo, trinity, 0, {'from': morpheus})

    assert farm_token.balanceOf(neo) == sender_balance
    assert farm_token.balanceOf(morpheus) == receiver_balance


def test_no_approval(farm_token, neo, morpheus, trinity, oracle):
    balance = farm_token.balanceOf(neo)
    with brownie.reverts():
        farm_token.transferFrom(
            trinity, oracle, balance, {'from': morpheus})


def test_revoked_approval(farm_token, neo, morpheus, trinity):
    balance = farm_token.balanceOf(neo)
    farm_token.approve(morpheus, 0, {'from': neo})

    with brownie.reverts():
        farm_token.transferFrom(neo, trinity, balance, {'from': morpheus})


def test_insufficient_approval(farm_token, neo, morpheus, trinity):
    balance = farm_token.balanceOf(neo)

    farm_token.approve(morpheus, balance - 1, {'from': neo})
    with brownie.reverts():
        farm_token.transferFrom(neo, trinity, balance, {'from': morpheus})


def test_transfer_to_self_no_approval(farm_token, neo, minter):
    amount = farm_token.balanceOf(neo)

    with brownie.reverts():
        farm_token.transferFrom(neo, neo, amount, {'from': neo})


def test_transfer_to_self(farm_token, neo):
    sender_balance = farm_token.balanceOf(neo)
    amount = sender_balance

    farm_token.approve(neo, sender_balance, {'from': neo})
    farm_token.transferFrom(neo, neo, amount, {'from': neo})

    assert farm_token.balanceOf(neo) == sender_balance
    assert farm_token.allowance(neo, neo) == sender_balance - amount


def test_insufficient_balance(farm_token, neo, morpheus, trinity):
    balance = farm_token.balanceOf(morpheus)

    farm_token.approve(neo, balance + 1, {'from': morpheus})
    with brownie.reverts():
        farm_token.transferFrom(
            morpheus, trinity, balance + 1, {'from': neo})


def test_transfer_zero_tokens_without_approval(farm_token, neo, morpheus, trinity):
    sender_balance = farm_token.balanceOf(morpheus)
    receiver_balance = farm_token.balanceOf(trinity)

    farm_token.transferFrom(morpheus, trinity, 0, {'from': neo})

    assert farm_token.balanceOf(morpheus) == sender_balance
    assert farm_token.balanceOf(trinity) == receiver_balance


def test_transfer_full_balance(farm_token, neo, morpheus, trinity):
    amount = farm_token.balanceOf(morpheus)
    receiver_balance = farm_token.balanceOf(trinity)

    farm_token.approve(neo, amount, {'from': morpheus})
    farm_token.transferFrom(morpheus, trinity, amount, {'from': neo})

    assert farm_token.balanceOf(morpheus) == 0
    assert farm_token.balanceOf(trinity) == receiver_balance + amount


@given(amount=strategy('uint256', min_value=1, max_value=10000*10**18))
def test_approve_minter(farm_token, neo, oracle, amount, minter):
    sender_balance = farm_token.balanceOf(neo)
    receiver_balance = farm_token.balanceOf(oracle)
    caller_balance = farm_token.balanceOf(minter)
    total_supply = farm_token.totalSupply()

    farm_token.approve(neo, 0, {'from': oracle})
    farm_token.approve(oracle, 0, {'from': neo})
    farm_token.transferFrom(
        neo, oracle, amount, {'from': minter})

    assert farm_token.balanceOf(neo) == sender_balance - amount
    assert farm_token.balanceOf(oracle) == receiver_balance + amount
    assert farm_token.balanceOf(minter) == caller_balance
    assert farm_token.totalSupply() == total_supply
