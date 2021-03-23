def test_stake_strategy_only(curve_staker_mocked, exception_tester, deployer):
    exception_tester("reaperStrategy only", curve_staker_mocked.stake, 1, {'from': deployer})


def test_unstake_strategy_only(curve_staker_mocked, exception_tester, deployer):
    exception_tester("reaperStrategy only", curve_staker_mocked.unstake, 1, {'from': deployer})


def test_claim_strategy_only(curve_staker_mocked, exception_tester, deployer):
    exception_tester("reaperStrategy only", curve_staker_mocked.claim, {'from': deployer})


def test_set_strategy_zero_address(curve_staker_mocked, exception_tester, ZERO_ADDRESS, deployer):
    exception_tester("zero address", curve_staker_mocked.setReaperStrategy, ZERO_ADDRESS, {'from': deployer})


def test_set_strategy_not_owner(curve_staker_mocked, ownable_exception_tester, deployer, morpheus):
    ownable_exception_tester(curve_staker_mocked.setReaperStrategy, deployer, {'from': morpheus})


def test_set_strategy(curve_staker_mocked, exception_tester, ZERO_ADDRESS, deployer):
    assert curve_staker_mocked.reaperStrategy() == ZERO_ADDRESS
    curve_staker_mocked.setReaperStrategy(deployer, {'from': deployer})
    assert curve_staker_mocked.reaperStrategy() == deployer


def test_stake(curve_staker_mocked, curve_gauge_mock, curve_minter_mock, lp_token, crv_token_mock, deployer, morpheus, chain, week):
    # fill minter mock with the money
    crv_token_mock.transfer(curve_minter_mock, 10 ** 18, {'from': deployer})

    # deployer <=> reaper strategy
    # give approve for curve_staker_mocked from reaper strategy TODO: maybe add that automatically
    lp_token.approve(curve_staker_mocked, 2 ** 256 - 1, {'from': deployer})

    tx1 = curve_staker_mocked.stake(1000, {'from': deployer})

    chain.mine(1, chain.time() + week)

    tx2 = curve_staker_mocked.claim(morpheus, {'from': deployer})

    assert tx2.return_value == 1000 * (tx2.timestamp - tx1.timestamp)
    assert crv_token_mock.balanceOf(morpheus) == tx2.return_value

    tx3 = curve_staker_mocked.stake(8000, {'from': deployer})

    chain.mine(1, chain.time() + week)

    tx4 = curve_staker_mocked.claim(morpheus, {'from': deployer})

    assert tx4.return_value == 9000 * (tx4.timestamp - tx3.timestamp) + 1000 * (tx3.timestamp - tx2.timestamp)
    assert crv_token_mock.balanceOf(morpheus) == tx4.return_value + tx2.return_value

    chain.mine(1, tx4.timestamp + week)

    tx5 = curve_staker_mocked.claim(morpheus, {'from': deployer})

    assert crv_token_mock.balanceOf(morpheus) == tx5.return_value + tx4.return_value + tx2.return_value
    assert tx5.return_value == 9000 * (tx5.timestamp - tx4.timestamp)

    chain.mine(1, tx5.timestamp + 2 * week)

    tx6 = curve_staker_mocked.unstake(9000, morpheus, {'from': deployer})

    assert lp_token.balanceOf(morpheus) == 9000

    chain.mine(1, tx6.timestamp + week)

    tx7 = curve_staker_mocked.claim(morpheus, {'from': deployer})

    assert crv_token_mock.balanceOf(morpheus) == tx7.return_value + tx5.return_value + tx4.return_value + tx2.return_value
    assert tx7.return_value == 9000 * (tx6.timestamp - tx5.timestamp)

    chain.mine(1, tx6.timestamp + week)

    tx8 = curve_staker_mocked.claim(morpheus, {'from': deployer})

    assert tx8.return_value == 0
