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

    assert usdn_mpool_gauge.claimable_tokens(curve_staker).return_value // 10 ** 18 >= 5 * 10 ** 6
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

    assert usdn_mpool_gauge.claimable_tokens(curve_staker).return_value // 10 ** 18 >= 16 * 10 ** 6
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


def test_deposit_crv_to_voting_escrow(farm_contracts, deployer, morpheus, chain, day, week, year, exception_tester):
    curve_staker = farm_contracts['curve_staker']
    curve_voting_escrow = farm_contracts['curve_voting_escrow']
    curve_voting_escrow_check_list = farm_contracts['curve_voting_escrow_check_list']
    crv = farm_contracts['crv']

    crv_value = 10 ** 19
    assert crv.balanceOf(deployer) > 10 ** 19
    assert curve_staker.lockingPeriod() == year

    exception_tester("owner only", curve_staker.setLockingPeriod, 5 * week, {'from': morpheus})
    curve_staker.setLockingPeriod(5 * week, {'from': deployer})

    crv.approve(curve_staker, crv_value, {'from': deployer})
    exception_tester("Smart contract depositors not allowed", curve_staker.depositToEscrow, crv_value, {'from': deployer})

    # add curve_staker to 
    curve_voting_escrow_check_list.addAddress(curve_staker, {'from': deployer})

    exception_tester("no unlocked amount for renewal", curve_staker.depositToEscrow, crv_value, True, {'from': deployer})

    tx1 = curve_staker.depositToEscrow(crv_value, {'from': deployer})

    assert curve_staker.lockUntilTimestamp() == curve_staker.lockUntilTimestampFor(deployer)
    assert curve_voting_escrow.locked(curve_staker) == [crv_value, curve_staker.lockUntilTimestamp()]
    assert crv.balanceOf(curve_staker) == 0
    assert curve_voting_escrow.balanceOf(curve_staker) > 0
    last_vecrv_balance = curve_voting_escrow.balanceOf(curve_staker)

    chain.mine(1, tx1.timestamp + week)
    crv.transfer(morpheus, crv_value, {'from': deployer})
    crv.approve(curve_staker, crv_value, {'from': morpheus})

    exception_tester("no unlocked amount for renewal", curve_staker.depositToEscrow, crv_value, True, {'from': morpheus})

    tx2 = curve_staker.depositToEscrow(crv_value, {'from': morpheus})

    assert curve_staker.lockUntilTimestampFor(deployer) == curve_staker.lockUntilTimestampFor(morpheus)
    assert curve_voting_escrow.locked(curve_staker) == [2 * crv_value, curve_staker.lockUntilTimestamp()]
    assert crv.balanceOf(curve_staker) == 0
    assert curve_voting_escrow.balanceOf(curve_staker) > 0
    assert curve_voting_escrow.balanceOf(curve_staker) > last_vecrv_balance

    exception_tester("withdraw is locked", curve_staker.withdrawFromEscrow, {'from': deployer})
    exception_tester("withdraw is locked", curve_staker.withdrawFromEscrow, {'from': morpheus})

    # lock is finished
    chain.mine(1, curve_staker.lockUntilTimestamp() + 1)

    assert curve_voting_escrow.balanceOf(curve_staker) == 0

    exception_tester("", curve_staker.withdrawFromEscrow, {'from': deployer})
    exception_tester("", curve_staker.withdrawFromEscrow, {'from': morpheus})

    # deployer has unlocked amount - so renewal or withdraw is needed
    exception_tester("withdrawal unlocked amount or renewal is needed", curve_staker.depositToEscrow, crv_value, False, {'from': deployer})
    exception_tester("withdrawal extra unlocked amount is needed", curve_staker.depositToEscrow, crv_value // 2, True, {'from': deployer})
    
    crv.approve(curve_staker, crv_value, {'from': deployer})
    tx3 = curve_staker.depositToEscrow(2 * crv_value, True, {'from': deployer})

    assert curve_staker.lockUntilTimestampFor(deployer) == curve_staker.lockUntilTimestamp()
    assert curve_voting_escrow.locked(curve_staker) == [2 * crv_value, curve_staker.lockUntilTimestamp()]
    assert crv.balanceOf(curve_staker) == crv_value
    assert curve_voting_escrow.balanceOf(curve_staker) > 0

    # withdraw for morpheus
    curve_staker.withdrawFromEscrow({'from': morpheus})

    assert crv.balanceOf(morpheus) == crv_value
    assert crv.balanceOf(curve_staker) == 0

    # lock is finished
    chain.mine(1, curve_staker.lockUntilTimestamp() + 1)

    # enable new lock
    crv.approve(curve_staker, 1, {'from': morpheus})
    curve_staker.depositToEscrow(1, False, {'from': morpheus})

    # withdraw for deployer
    curve_staker.withdrawFromEscrow({'from': deployer})

    assert curve_staker.lockUntilTimestampFor(morpheus) == curve_staker.lockUntilTimestamp()
    assert curve_voting_escrow.locked(curve_staker) == [1, curve_staker.lockUntilTimestamp()]
    assert crv.balanceOf(curve_staker) == 0
