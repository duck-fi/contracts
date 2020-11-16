import brownie
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=100000*10**18))
def test_burn_affects_balance(token, supply_controller, neo, amount):
    total_supply = token.totalSupply()
    balance = token.balanceOf(neo)
    token.burnFrom(neo, amount, {'from': supply_controller})
    assert token.balanceOf(neo) == balance - amount
    assert token.totalSupply() == total_supply - amount


def test_burn_underflow(token, supply_controller, neo):
    amount = token.balanceOf(neo) + 1
    with brownie.reverts():
        token.burnFrom(neo, amount, {'from': supply_controller})


@given(amount=strategy('uint256', min_value=1))
def test_burn_not_minter(token, neo, amount):
    with brownie.reverts():
        token.burnFrom(neo, amount, {'from': neo})


def test_burn_zero_address(ZERO_ADDRESS, token, neo, supply_controller):
    balance = token.balanceOf(neo)
    token.transfer(ZERO_ADDRESS, balance, {'from': neo})

    with brownie.reverts():
        token.burnFrom(ZERO_ADDRESS, balance, {'from': supply_controller})
