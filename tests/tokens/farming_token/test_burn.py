import brownie
from math import floor
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=2, max_value=10000*10**18))
def test_burn_affects_balance(farming_token, supply_controller, neo, amount):
    total_supply = farming_token.totalSupply()
    balance = farming_token.balanceOf(neo)

    farming_token.burnFrom(neo, amount, {'from': supply_controller})
    assert farming_token.balanceOf(neo) == balance - amount
    assert farming_token.totalSupply() == total_supply - amount

    burnAmount = floor(amount / 2)
    farming_token.burn(burnAmount, {'from': neo})
    assert farming_token.balanceOf(neo) == balance - amount - burnAmount
    assert farming_token.totalSupply() == total_supply - amount - burnAmount


def test_burn_from_underflow(farming_token, supply_controller, neo):
    amount = farming_token.balanceOf(neo) + 1
    with brownie.reverts():
        farming_token.burnFrom(neo, amount, {'from': supply_controller})


def test_burn_underflow(farming_token, supply_controller, neo):
    amount = farming_token.balanceOf(neo) + 1
    with brownie.reverts():
        farming_token.burn(amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_burn_not_minter(farming_token, neo, amount):
    with brownie.reverts():
        farming_token.burnFrom(neo, amount, {'from': neo})


def test_burn_from_zero_address(ZERO_ADDRESS, farming_token, neo, supply_controller):
    balance = farming_token.balanceOf(neo)
    farming_token.transfer(ZERO_ADDRESS, balance, {'from': neo})

    with brownie.reverts():
        farming_token.burnFrom(ZERO_ADDRESS, balance, {
                               'from': supply_controller})
