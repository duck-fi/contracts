#!/usr/bin/python3

import brownie
from brownie.test import given, strategy


def test_only_supply_controller(farming_token, supply_controller, neo):
    with brownie.reverts():
        farming_token.set_supply_controller(neo, {'from': neo})


def test_set_supply_controller(farming_token, supply_controller, neo):
    farming_token.set_supply_controller(neo, {'from': supply_controller})
    farming_token.set_supply_controller(supply_controller, {'from': neo})


def test_transferFrom_without_approval(farming_token, supply_controller, neo, morpheus):
    balance = farming_token.balanceOf(neo)
    amount = balance / 2

    # supply_controller should be able to call transferFrom without prior approval
    farming_token.transferFrom(neo, morpheus, amount, {
                               'from': supply_controller})

    assert farming_token.balanceOf(neo) == balance - amount
    assert farming_token.balanceOf(morpheus) == amount


@given(amount=strategy('uint256', min_value=1))
def test_mint_affects_balance(farming_token, trinity, supply_controller, amount):
    farming_token.mint(trinity, amount, {'from': supply_controller})
    assert farming_token.balanceOf(trinity) == amount


@given(amount=strategy('uint256', min_value=1))
def test_mint_affects_totalSupply(farming_token, supply_controller, trinity, amount):
    total_supply = farming_token.totalSupply()
    farming_token.mint(trinity, amount, {'from': supply_controller})
    assert farming_token.totalSupply() == total_supply + amount


def test_mint_overflow(farming_token, supply_controller, trinity):
    amount = 2**256 - farming_token.totalSupply()
    with brownie.reverts():
        farming_token.mint(trinity, amount, {'from': supply_controller})


@given(amount=strategy('uint256', min_value=1))
def test_mint_not_minter(farming_token, neo, amount):
    with brownie.reverts():
        farming_token.mint(neo, amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_mint_zero_address(ZERO_ADDRESS, farming_token, supply_controller, amount):
    with brownie.reverts():
        farming_token.mint(ZERO_ADDRESS, amount, {'from': supply_controller})
