def test_reaper_deposit_withdraw(farm_contracts, deployer, morpheus, trinity, chain, day, week, ZERO_ADDRESS, exception_tester):
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

    assert usdn_mpool_gauge.claimable_tokens(curve_staker).return_value // 10 ** 18 >= 5 * 10 ** 6
    assert abs(usdn_mpool_gauge.inflation_rate() - 8.7 * 10 ** 18) <= 0.1 * 10 ** 18

    # reap crv, buyback and burn ducks
    tx2 = reaper.reap({'from': deployer})

    assert len(tx2.events) == 12
    assert tx2.return_value > 0
    assert tx2.events['Transfer'][len(tx2.events['Transfer']) - 1].values() == [curve_strategy_v1, ZERO_ADDRESS, tx2.return_value]

    # withdraw is not activated yet
    exception_tester("withdraw is locked", reaper.withdraw, 500, {'from': morpheus})

    # activate withdraw on strategy
    curve_strategy_v1.activate({'from': deployer})

    # withdraw
    tx3 = reaper.withdraw(1000, {'from': deployer})
    
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 0
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 0
    assert usdn_mpool_lp.balanceOf(reaper) == 0
    assert usdn_mpool_lp.balanceOf(curve_strategy_v1) == 0
    assert usdn_mpool_lp.balanceOf(curve_staker) == 0
    assert usdn_mpool_lp.balanceOf(usdn_mpool_gauge) == 0
    assert usdn_mpool_gauge.balanceOf(curve_staker) == 0
