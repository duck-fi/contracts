#!/usr/bin/python3

import brownie
from brownie.test import given, strategy


def test_only_minter(farm_token, minter, neo):
    with brownie.reverts():
        farm_token.setMinter(neo, {'from': neo})


def test_set_minter(farm_token, minter, neo):
    farm_token.setMinter(neo, {'from': minter})
    farm_token.setMinter(minter, {'from': neo})


def test_transferFrom_without_approval(farm_token, minter, neo, morpheus):
    balance = farm_token.balanceOf(neo)
    amount = balance / 2

    # minter should be able to call transferFrom without prior approval
    farm_token.transferFrom(neo, morpheus, amount, {
                               'from': minter})

    assert farm_token.balanceOf(neo) == balance - amount
    assert farm_token.balanceOf(morpheus) == amount


@given(amount=strategy('uint256', min_value=1))
def test_mint_affects_balance(farm_token, minter, trinity, amount):
    farm_token.mint(trinity, amount, {'from': minter})
    assert farm_token.balanceOf(trinity) == amount


@given(amount=strategy('uint256', min_value=1))
def test_mint_affects_totalSupply(farm_token, minter, trinity, amount):
    total_supply = farm_token.totalSupply()
    farm_token.mint(trinity, amount, {'from': minter})
    assert farm_token.totalSupply() == total_supply + amount


def test_mint_overflow(farm_token, minter, trinity):
    amount = 2**256 - farm_token.totalSupply()
    with brownie.reverts():
        farm_token.mint(trinity, amount, {'from': minter})


@given(amount=strategy('uint256', min_value=1))
def test_mint_not_minter(farm_token, neo, amount):
    with brownie.reverts():
        farm_token.mint(neo, amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_mint_zero_address(ZERO_ADDRESS, farm_token, minter, amount):
    with brownie.reverts():
        farm_token.mint(ZERO_ADDRESS, amount, {'from': minter})
