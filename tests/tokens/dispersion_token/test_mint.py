import brownie
from brownie.test import given, strategy


def test_only_supply_controller(token, supply_controller, neo):
    with brownie.reverts():
        token.set_supply_controller(neo, {'from': neo})


def test_set_supply_controller(token, supply_controller, neo):
    token.set_supply_controller(neo, {'from': supply_controller})
    token.set_supply_controller(supply_controller, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_transferFrom_without_approval(token, supply_controller, neo, morpheus, amount):
    balance = token.balanceOf(neo)

    # supply_controller should be able to call transferFrom without prior approval
    token.transferFrom(neo, morpheus, amount, {'from': supply_controller})

    assert token.balanceOf(neo) == balance - amount
    assert token.balanceOf(morpheus) == amount


@given(amount=strategy('uint256', min_value=1))
def test_mint_affects_balance(token, trinity, supply_controller, amount):
    token.mint(trinity, amount, {'from': supply_controller})
    assert token.balanceOf(trinity) == amount


@given(amount=strategy('uint256', min_value=1))
def test_mint_affects_totalSupply(token, supply_controller, trinity, amount):
    total_supply = token.totalSupply()
    token.mint(trinity, amount, {'from': supply_controller})
    assert token.totalSupply() == total_supply + amount


def test_mint_overflow(token, supply_controller, trinity):
    amount = 2**256 - token.totalSupply()
    with brownie.reverts():
        token.mint(trinity, amount, {'from': supply_controller})


@given(amount=strategy('uint256', min_value=1))
def test_mint_not_minter(token, neo, amount):
    with brownie.reverts():
        token.mint(neo, amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_mint_zero_address(ZERO_ADDRESS, token, supply_controller, amount):
    with brownie.reverts():
        token.mint(ZERO_ADDRESS, amount, {'from': supply_controller})
