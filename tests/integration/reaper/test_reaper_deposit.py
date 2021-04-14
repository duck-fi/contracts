def test_reaper_deposit_withdraw(farm_contracts, deployer, morpheus, trinity, chain, day, week, exception_tester):
    usdn_mpool_lp = farm_contracts['usdn_mpool_lp']
    reaper = farm_contracts['usdn_mpool_reaper']
    curve_strategy_v1 = farm_contracts['curve_strategy_v1']
    curve_staker = farm_contracts['curve_staker']
    usdn_mpool_gauge = farm_contracts['usdn_mpool_gauge']

    usdn_mpool_lp.approve(reaper, 1000, {'from': deployer})
    tx1 = reaper.deposit(1000, {'from': deployer})

    assert reaper.balances(deployer) == 1000
    assert usdn_mpool_lp.balanceOf(reaper) == 0
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 1000
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 1000

    chain.mine(1, tx1.timestamp + 2 * week)

    assert abs(usdn_mpool_gauge.claimable_tokens(curve_staker).return_value // 10**18 - 5 * 10 ** 6) <= 10 ** 6
    assert abs(usdn_mpool_gauge.inflation_rate() - 8.7 * 10 ** 18) <= 0.1 * 10 ** 18

    usdn_mpool_lp.transfer(morpheus, 1000, {'from': deployer})
    usdn_mpool_lp.approve(reaper, 1000, {'from': morpheus})
    tx2 = reaper.deposit(1000, morpheus, True, {'from': morpheus})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.totalBalances() == 2000
    assert usdn_mpool_lp.balanceOf(reaper) == 1000
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 1000
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 1000

    tx3 = reaper.invest({'from': trinity})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.totalBalances() == 2000
    assert usdn_mpool_lp.balanceOf(reaper) == 0
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 2000
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 2000

    chain.mine(1, tx3.timestamp + 2 * week)

    assert abs(usdn_mpool_gauge.claimable_tokens(curve_staker).return_value // 10**18 - 16 * 10 ** 6) <= 10 ** 6
    assert abs(usdn_mpool_gauge.inflation_rate() - 8.7 * 10 ** 18) <= 0.1 * 10 ** 18

    usdn_mpool_lp.transfer(trinity, 1000, {'from': deployer})
    usdn_mpool_lp.approve(reaper, 1000, {'from': trinity})
    tx4 = reaper.deposit(1000, trinity, True, {'from': trinity})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.balances(trinity) == 1000
    assert reaper.totalBalances() == 3000
    assert usdn_mpool_lp.balanceOf(reaper) == 1000
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 2000
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 2000

    # withdraw is not activated yet
    exception_tester("withdraw is locked", reaper.withdraw, 500, {'from': morpheus})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.balances(trinity) == 1000
    assert reaper.totalBalances() == 3000
    assert usdn_mpool_lp.balanceOf(reaper) == 1000
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 2000
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 2000

    # activate withdraw on strategy
    curve_strategy_v1.activate({'from': deployer})

    # withdraw
    tx5 = reaper.withdraw(500, {'from': morpheus})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 500
    assert reaper.balances(trinity) == 1000
    assert reaper.totalBalances() == 2500
    assert usdn_mpool_lp.balanceOf(reaper) == 500
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 2000
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 2000

    tx6 = reaper.withdraw(1000, {'from': trinity})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 500
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 1500
    assert usdn_mpool_lp.balanceOf(reaper) == 0
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 1500
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 1500

    tx7 = reaper.withdraw(1000, {'from': deployer})
    
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 500
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 500
    assert usdn_mpool_lp.balanceOf(reaper) == 0
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 500
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 500

    tx7 = reaper.withdraw(500, {'from': morpheus})

    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 0
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 0
    assert usdn_mpool_lp.balanceOf(reaper) == 0
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 0
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 0
