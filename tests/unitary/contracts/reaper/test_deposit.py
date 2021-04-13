from brownie.test import given, strategy


def test_insufficient_funds_deposit(reaper, thomas, exception_tester):
    exception_tester('', reaper.deposit, 1, {'from': thomas})


def test_insufficient_funds_withdraw(reaper, thomas, exception_tester):
    exception_tester('', reaper.withdraw, 1, {'from': thomas})


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_deposit(farm_token, lp_token, controller, reaper, voting_controller, deployer, chain, day, amount):
    initial_balance = lp_token.balanceOf(deployer)
    controller.startEmission(voting_controller, 0, {'from': deployer})

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
