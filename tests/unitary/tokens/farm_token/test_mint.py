#!/usr/bin/python3

import pytest
import brownie
from brownie.test import given, strategy

# TODO consider to move into shared place/module
def to_raw_farm_token(dec_amount: float) -> int:
    return dec_amount * (10 ** FARM_TOKEN_DECIMALS)

def to_dec_farm_token(raw_amount: int) -> float:
    return raw_amount / (10 ** FARM_TOKEN_DECIMALS)

FARM_TOKEN_DECIMALS = 18
FARM_TOKEN_INITIAL_SUPPLY_DEC = 100_000
INITIAL_EMISSION_DEC = 1_000_000
INITIAL_EMISSION_RAW = to_raw_farm_token(INITIAL_EMISSION_DEC)
SECONDS_IN_YEAR = 86_400 * 365
EMISSION_REDUCTION_SECONDS = SECONDS_IN_YEAR


def test_fail_to_update_minter_not_by_owner(farm_token, minter, neo, morpheus):
    with brownie.reverts("owner only"):
        farm_token.setMinter(morpheus, {'from': minter})


def test_success_update_minter_by_owner(farm_token, minter, neo, morpheus):
    farm_token.setMinter(morpheus, {'from': neo})
    farm_token.setMinter(minter, {'from': neo})


def test_transferFrom_without_approval_by_minter(farm_token, minter, neo, morpheus):
    balance = farm_token.balanceOf(neo)
    amount = balance / 2

    # minter should be able to call transferFrom without prior approval
    farm_token.transferFrom(neo, morpheus, amount, {
                               'from': minter})

    assert farm_token.balanceOf(neo) == balance - amount
    assert farm_token.balanceOf(morpheus) == amount


@given(amount=strategy('uint256', min_value=1))
def test_fail_to_mint_beforeStartEmission(farm_token, minter, trinity, amount):
    with brownie.reverts("exceeds allowable mint amount"):
        farm_token.mint(trinity, amount, {'from': minter})


def assert_emission(farm_token, expected_yearEmission):
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()
    tx = farm_token.yearEmission()
    assert tx.return_value == expected_yearEmission, "invalid yearEmission"
    tx_emissionIntegral = farm_token.emissionIntegral()
    dt = tx_emissionIntegral.timestamp - lastEmissionUpdateTimestamp
    assert tx_emissionIntegral.return_value == dt * expected_yearEmission / SECONDS_IN_YEAR, "invalid emissionIntegral"


def test_yearEmission_beforeStartEmission(farm_token):
    assert_emission(farm_token, 0)


def test_yearEmission_inNextYear_beforeStartEmission(farm_token, chain):
    chain.mine(100, chain.time() + EMISSION_REDUCTION_SECONDS + 100)
    test_yearEmission_beforeStartEmission(farm_token)


def test_fail_to_startEmission_not_by_owner(farm_token, minter):
    with brownie.reverts("owner only"):
        farm_token.startEmission({'from': minter})


def test_success_startEmission(farm_token, neo, chain):
    t1 = chain.time()
    farm_token.startEmission({'from': neo})
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()
    startEmissionTimestamp = farm_token.startEmissionTimestamp()
    t2 = chain.time()

    assert lastEmissionUpdateTimestamp >= t1 and lastEmissionUpdateTimestamp <= t2
    assert startEmissionTimestamp >= t1 and startEmissionTimestamp <= t2
    assert_emission(farm_token, INITIAL_EMISSION_RAW)


def test_emissionIntegral_progress(farm_token, chain, trinity, minter):
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()

    for quarter in range(1, 12): # 3 years 
        prev_val = farm_token.emissionIntegral().return_value

        time_move = quarter * SECONDS_IN_YEAR / 4
        chain.mine(100, lastEmissionUpdateTimestamp + time_move)

        year_emission = farm_token.yearEmission().return_value
        quater_max_minting_amount = year_emission / 4

        # emission integral always increase its' value
        new_val = farm_token.emissionIntegral().return_value
        assert new_val > prev_val, "current emissionIntegral value must be greater than prev: quarter={quarter} time_move={time_move}"

        # mint process affects user's balance and total supply
        balance_before = farm_token.balanceOf(trinity)
        total_supply = farm_token.totalSupply()
        farm_token.mint(trinity, quater_max_minting_amount, {'from': minter})
        assert farm_token.balanceOf(trinity) == balance_before + quater_max_minting_amount, "minting process affects user's balance: quarter={quarter}"
        assert farm_token.totalSupply() == total_supply + quater_max_minting_amount, "minting process affects total supply: quarter={quarter}"

        # fail to mint more than allowed
        with brownie.reverts("exceeds allowable mint amount"):
            farm_token.mint(trinity, to_raw_farm_token(100), {'from': minter})


def test_emission_overflow(farm_token, minter, trinity):
    amount = farm_token.yearEmission().return_value + 1
    with brownie.reverts("exceeds allowable mint amount"):
        farm_token.mint(trinity, amount, {'from': minter})


@given(amount=strategy('uint256', min_value=1))
def test_mint_not_minter(farm_token, neo, amount):
    with brownie.reverts("not minter"):
        farm_token.mint(neo, amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_mint_zero_address(ZERO_ADDRESS, farm_token, minter, amount):
    with brownie.reverts("zero address"):
        farm_token.mint(ZERO_ADDRESS, amount, {'from': minter})
