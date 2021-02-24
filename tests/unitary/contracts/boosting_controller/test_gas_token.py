from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_vote_gas_reducing_not_valid_token(boosting_controller_mocked, farm_token, exception_tester, deployer, amount, week):
    farm_token.approve(boosting_controller_mocked, amount, {'from': deployer})
    exception_tester("unsupported gas token", boosting_controller_mocked.boost,
                     farm_token, 1, 2 * week, farm_token, {'from': deployer})
    exception_tester("unsupported gas token", boosting_controller_mocked.unboost,
                     farm_token, farm_token, {'from': deployer})


@given(amount=strategy('uint256', min_value=10 ** 10, max_value=10 ** 13))
def test_boost_farm_token(boosting_controller_mocked, farm_token, chi_token, deployer, amount, week, chain):
    minLockTime = 2 * week

    chi_token.mint(10, {'from': deployer})
    chi_token.approve(boosting_controller_mocked, 10, {'from': deployer})
    farm_token.approve(boosting_controller_mocked, 0, {'from': deployer})
    farm_token.approve(boosting_controller_mocked,
                       5 * amount, {'from': deployer})
    tx1 = boosting_controller_mocked.boost(
        farm_token, amount, minLockTime, chi_token, {'from': deployer})
    assert tx1.return_value is None
    assert len(tx1.events) == 4
    assert tx1.events["Boost"].values() == [farm_token, deployer, amount]
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert boosting_controller_mocked.boostIntegral() == 0
    assert 10 - chi_token.balanceOf(deployer) == 5

    chain.mine(1, chain.time() + 2 * minLockTime + 1)

    tx2 = boosting_controller_mocked.unboost(
        farm_token, chi_token, {'from': deployer})
    assert tx2.return_value is None
    assert len(tx2.events) == 4
    assert tx2.events["Unboost"].values(
    ) == [farm_token, deployer, amount]
    assert boosting_controller_mocked.balances(farm_token, deployer) == 0
    assert boosting_controller_mocked.coinBalances(farm_token) == 0
    assert 5 - chi_token.balanceOf(deployer) == 4
