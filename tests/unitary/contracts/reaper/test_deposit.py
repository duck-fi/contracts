from brownie.test import given, strategy


def test_insufficient_funds_deposit(reaper, thomas, exception_tester):
    exception_tester('', reaper.deposit, 1, {'from': thomas})


def test_insufficient_funds_withdraw(reaper, thomas, exception_tester):
    exception_tester('', reaper.withdraw, 1, {'from': thomas})


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_deposit(farm_token, lp_token, controller, reaper, voting_controller, deployer, chain, day, amount):
    initial_balance = lp_token.balanceOf(deployer)
    controller.startEmission(0, {'from': deployer})

    chain.mine(1, chain.time())
    voting_controller.snapshot({'from': deployer})

    lp_token.approve(reaper, 2 * amount, {'from': deployer})
    reaper.deposit(amount, {'from': deployer})
    assert lp_token.balanceOf(reaper) == amount
    assert lp_token.balanceOf(deployer) == initial_balance - amount

    chain.mine(1, chain.time() + day)
    reaper.deposit(amount, {'from': deployer})
    assert lp_token.balanceOf(reaper) == 2 * amount
    assert lp_token.balanceOf(deployer) == initial_balance - 2 * amount

    chain.mine(1, chain.time() + day)
    reaper.withdraw(2 * amount, {'from': deployer})
    assert lp_token.balanceOf(reaper) == 0
    assert lp_token.balanceOf(deployer) == initial_balance


@given(amount=strategy('uint256', min_value=10, max_value=1_000))
def test_deposit_approve(farm_token, lp_token, controller, reaper, voting_controller, deployer, morpheus, chain, day, amount):
    initial_balance = lp_token.balanceOf(deployer)

    lp_token.approve(reaper, 2 * amount, {'from': deployer})
    reaper.depositApprove(deployer, 2 * amount, {'from': morpheus})
    assert reaper.depositAllowance(morpheus, deployer) == 2 * amount

    reaper.deposit(amount, morpheus, {'from': deployer})
    assert lp_token.balanceOf(reaper) == amount
    assert lp_token.balanceOf(deployer) == initial_balance - amount
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == amount
    assert reaper.depositAllowance(morpheus, deployer) == amount

    chain.mine(1, chain.time() + day)
    reaper.deposit(amount, morpheus, {'from': deployer})
    assert lp_token.balanceOf(reaper) == 2 * amount
    assert lp_token.balanceOf(deployer) == initial_balance - 2 * amount
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 2 * amount
    assert reaper.depositAllowance(morpheus, deployer) == 0

    chain.mine(1, chain.time() + day)
    reaper.withdraw(2 * amount, {'from': morpheus})
    assert lp_token.balanceOf(reaper) == 0
    assert lp_token.balanceOf(deployer) == initial_balance - 2 * amount
    assert lp_token.balanceOf(morpheus) == 2 * amount
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 0
    assert reaper.depositAllowance(morpheus, deployer) == 0


@given(amount=strategy('uint256', min_value=10, max_value=1_000))
def test_deposit_infinite_approve(farm_token, lp_token, controller, reaper, voting_controller, deployer, trinity, chain, day, amount, MAX_UINT256):
    initial_balance = lp_token.balanceOf(deployer)

    lp_token.approve(reaper, 2 * amount, {'from': deployer})
    reaper.depositApprove(deployer, MAX_UINT256, {'from': trinity})
    reaper.deposit(amount, trinity, {'from': deployer})
    assert lp_token.balanceOf(reaper) == amount
    assert lp_token.balanceOf(deployer) == initial_balance - amount
    assert reaper.balances(deployer) == 0
    assert reaper.balances(trinity) == amount
    assert reaper.depositAllowance(trinity, deployer) == MAX_UINT256

    chain.mine(1, chain.time() + day)
    reaper.deposit(amount, trinity, {'from': deployer})
    assert lp_token.balanceOf(reaper) == 2 * amount
    assert lp_token.balanceOf(deployer) == initial_balance - 2 * amount
    assert reaper.balances(deployer) == 0
    assert reaper.balances(trinity) == 2 * amount
    assert reaper.depositAllowance(trinity, deployer) == MAX_UINT256

    chain.mine(1, chain.time() + day)
    reaper.withdraw(2 * amount, {'from': trinity})
    assert lp_token.balanceOf(reaper) == 0
    assert lp_token.balanceOf(deployer) == initial_balance - 2 * amount
    assert lp_token.balanceOf(trinity) == 2 * amount
    assert reaper.balances(deployer) == 0
    assert reaper.balances(trinity) == 0
    assert reaper.depositAllowance(trinity, deployer) == MAX_UINT256
