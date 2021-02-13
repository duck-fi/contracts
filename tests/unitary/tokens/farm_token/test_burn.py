import brownie
from math import floor
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=2, max_value=10000*10**18))
def test_burn_affects_balance(farm_token, neo, amount, ZERO_ADDRESS):
    total_supply = farm_token.totalSupply()
    balance = farm_token.balanceOf(neo)

    tx = farm_token.burn(amount, {'from': neo})
    assert farm_token.balanceOf(neo) == balance - amount
    assert farm_token.totalSupply() == total_supply - amount
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [neo, ZERO_ADDRESS, amount]

    burnAmount = floor(amount / 2)
    farm_token.burn(burnAmount, {'from': neo})
    assert farm_token.balanceOf(neo) == balance - amount - burnAmount
    assert farm_token.totalSupply() == total_supply - amount - burnAmount


def test_burn_underflow(farm_token, neo):
    amount = farm_token.balanceOf(neo) + 1
    with brownie.reverts():
        farm_token.burn(amount, {'from': neo})


def test_burn_zero(farm_token, neo):
    balance = farm_token.balanceOf(neo)
    farm_token.burn(0, {'from': neo})
    assert balance == farm_token.balanceOf(neo)


@given(account=strategy('address'))
def test_burn_accounts(farm_token, account):
    balance = farm_token.balanceOf(account)
    farm_token.burn(balance, {'from': account})
    assert farm_token.balanceOf(account) == 0
