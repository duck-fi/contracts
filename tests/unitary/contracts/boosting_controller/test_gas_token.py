from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_vote_gas_reducing_not_valid_token(boosting_controller_mocked, boosting_token_mocked, exception_tester, deployer, amount, week):
    boosting_token_mocked.mint(deployer, amount, {'from': deployer})
    boosting_token_mocked.approve(
        boosting_controller_mocked, amount, {'from': deployer})
    exception_tester("unsupported gas token", boosting_controller_mocked.boost,
                     1, 2 * week, boosting_token_mocked, {'from': deployer})
    exception_tester("unsupported gas token", boosting_controller_mocked.unboost,
                     boosting_token_mocked, {'from': deployer})


@given(amount=strategy('uint256', min_value=10 ** 10, max_value=10 ** 13))
def test_boost_boosting_token(boosting_controller_mocked, boosting_token_mocked, chi_token, deployer, amount, week, chain):
    minLockTime = 2 * week

    chi_token.mint(10, {'from': deployer})
    chi_token.approve(boosting_controller_mocked, 10, {'from': deployer})

    boosting_token_mocked.mint(deployer, amount, {'from': deployer})
    boosting_token_mocked.approve(
        boosting_controller_mocked, 0, {'from': deployer})
    boosting_token_mocked.approve(
        boosting_controller_mocked, 5 * amount, {'from': deployer})

    tx1 = boosting_controller_mocked.boost(
        amount, minLockTime, chi_token, {'from': deployer})
    assert tx1.return_value is None
    assert len(tx1.events) == 4
    assert tx1.events["Boost"].values() == [deployer, amount, minLockTime]
    assert boosting_controller_mocked.balances(deployer) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert boosting_controller_mocked.boostIntegral() == 0
    assert 10 - chi_token.balanceOf(deployer) == 5

    chain.mine(1, chain.time() + 2 * minLockTime + 1)

    tx2 = boosting_controller_mocked.unboost(
        chi_token, {'from': deployer})
    assert tx2.return_value is None
    assert len(tx2.events) == 4
    assert tx2.events["Unboost"].values() == [deployer, amount]
    assert boosting_controller_mocked.balances(deployer) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert 5 - chi_token.balanceOf(deployer) == 3
