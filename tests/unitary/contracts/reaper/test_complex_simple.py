VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18


def test_complex_simple(farm_token, lp_token, reaper, voting_controller, deployer, morpheus, trinity, MAX_UINT256, chain, year, day):
    amount = 10**18
    lp_token.transfer(morpheus, 10 * amount, {'from': deployer})
    lp_token.transfer(trinity, 10 * amount, {'from': deployer})
    initial_balance = lp_token.balanceOf(deployer)
    lp_token.approve(reaper, MAX_UINT256, {'from': deployer})
    lp_token.approve(reaper, MAX_UINT256, {'from': morpheus})
    lp_token.approve(reaper, MAX_UINT256, {'from': trinity})
    init_ts = chain.time()
    chain.mine(1, init_ts)
    tx = farm_token.startEmission({'from': deployer})
    initial_emission_timestamp = tx.timestamp
    chain.mine(1, init_ts)
    tx = voting_controller.startVoting({'from': deployer})
    initial_voting_timestamp = tx.timestamp
    assert reaper.balances(deployer) == 0
    assert reaper.totalBalances() == 0
    assert reaper.balancesIntegral() == 0
    assert reaper.balancesIntegralFor(deployer) == 0
    assert reaper.unitCostIntegral() == 0
    assert reaper.lastUnitCostIntegralFor(deployer) == 0
    assert reaper.reapIntegral() == 0
    assert reaper.reapIntegralFor(deployer) == 0
    assert reaper.lastSnapshotTimestamp() == 0
    assert reaper.lastSnapshotTimestampFor(deployer) == 0
    assert reaper.emissionIntegral() == 0
    assert reaper.voteIntegral() == 0
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0

    # deposit amount for deployer
    chain.mine(1, init_ts)
    tx2 = reaper.deposit(amount, {'from': deployer})
    assert lp_token.balanceOf(reaper) == amount
    assert lp_token.balanceOf(deployer) == initial_balance - amount
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == 0
    assert reaper.balancesIntegralFor(deployer) == 0
    assert reaper.unitCostIntegral() == 0
    assert reaper.lastUnitCostIntegralFor(deployer) == 0
    assert reaper.reapIntegral() == 0
    assert reaper.reapIntegralFor(deployer) == 0
    assert reaper.lastSnapshotTimestamp() == tx2.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx2.timestamp
    assert reaper.emissionIntegral() == 0
    assert reaper.voteIntegral() == (tx2.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    init_vote_integral = reaper.voteIntegral()

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print(tx2.timestamp - initial_voting_timestamp)
    print("last_unit_cost_integral", last_unit_cost_integral)
    print("-------------")

    # 1st snapshot
    chain.mine(1, tx2.timestamp + day)
    tx3 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx3.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx3.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx3.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // reaper.balancesIntegral()
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER
    assert reaper.lastSnapshotTimestamp() == tx3.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx3.timestamp
    assert reaper.voteIntegral() == (tx3.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("last_unit_cost_integral", last_unit_cost_integral)
    print((tx3.timestamp - tx2.timestamp))
    print("last_reap_integral_deployer", last_reap_integral_deployer)
    print("-------------")

    # 2nd snapshot
    chain.mine(1, tx3.timestamp + day)
    tx4 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx4.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx4.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx4.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx4.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx4.timestamp
    assert reaper.voteIntegral() == (tx4.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("last_unit_cost_integral", last_unit_cost_integral)
    print((tx4.timestamp - tx2.timestamp))
    print("last_reap_integral_deployer", last_reap_integral_deployer)
    print("-------------")

    # 3rd snapshot
    chain.mine(1, tx4.timestamp + 3 * day)
    tx5 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx5.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx5.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx5.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx5.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx5.timestamp
    assert reaper.voteIntegral() == (tx5.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # 4th snapshot
    chain.mine(1, tx5.timestamp + 2 * day)
    tx6 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx6.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.voteIntegral() == (tx6.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("last_unit_cost_integral", last_unit_cost_integral)
    print("last_unit_cost_integral_deployer", last_unit_cost_integral_deployer)
    print((tx6.timestamp - tx2.timestamp))
    print("t", tx6.timestamp)
    print("dt", tx6.timestamp - tx2.timestamp)
    print("last_reap_integral_deployer", last_reap_integral_deployer)
    print("-------------")

    # deposit amount for morpheus (snapshot for deployer has not been done for a day)
    chain.mine(1, tx6.timestamp + day)
    tx7 = reaper.deposit(amount, {'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == amount * (tx7.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx6.timestamp - tx2.timestamp) # not updated for deployer
    assert reaper.balancesIntegralFor(morpheus) == 0
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx7.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(deployer) == last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) # not updated
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == 0
    assert reaper.lastSnapshotTimestamp() == tx7.timestamp 
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp # not updated
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx7.timestamp
    assert reaper.reapIntegral() == last_reap_integral_deployer # not updated
    assert reaper.voteIntegral() == (tx7.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("last_unit_cost_integral", reaper.unitCostIntegral())
    print("last_unit_cost_integral_deployer", reaper.lastUnitCostIntegralFor(deployer))
    print("last_unit_cost_integral_morpheus", reaper.lastUnitCostIntegralFor(morpheus))
    print("emissionIntegral", reaper.emissionIntegral())
    print("t", tx7.timestamp)
    print("dt", tx7.timestamp - tx2.timestamp)

    # 5th snapshot for both: 10 days for deployer and 2 day for morpheus
    # deployer should get EMISSION / 2 (no boost) / 10 (days) * 9 (8 (day) + 1 (2*0.5 day))  
    # morpheus should get EMISSION / 2 (no boost) / 10 (days) * 1 (2*0.5 day)
    chain.mine(1, tx7.timestamp + 2 * day)
    tx8 = reaper.snapshot({'from': deployer})
    chain.mine(1, tx7.timestamp + 2 * day)
    tx8 = reaper.snapshot({'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx8.timestamp - tx7.timestamp) + amount * (tx7.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx8.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral_deployer) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral_morpheus) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 10 * 9) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 10 * 1) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.lastSnapshotTimestamp() == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx8.timestamp
    assert reaper.voteIntegral() == (tx8.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("last_unit_cost_integral", reaper.unitCostIntegral())
    print("last_unit_cost_integral_deployer", reaper.lastUnitCostIntegralFor(deployer))
    print("last_unit_cost_integral_morpheus", reaper.lastUnitCostIntegralFor(morpheus))
    print("emissionIntegral", reaper.emissionIntegral())
    print("t", tx8.timestamp)
    print("dt", tx8.timestamp - tx2.timestamp)

    # 6th snapshot for both: 12 days for deployer and 4 day for morpheus
    # deployer should get EMISSION / 2 (no boost) / 12 (days) * 10 (8 (day) + 2 (4*0.5 day))  
    # morpheus should get EMISSION / 2 (no boost) / 12 (days) * 2  (4*0.5 day)
    chain.mine(1, tx8.timestamp + 2 * day)
    tx9 = reaper.snapshot({'from': deployer})
    chain.mine(1, tx8.timestamp + 2 * day)
    tx9 = reaper.snapshot({'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx9.timestamp - tx7.timestamp) + amount * (tx7.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx9.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral_deployer) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral_morpheus) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 12 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 12 * 2)  <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.lastSnapshotTimestamp() == tx9.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx9.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx9.timestamp
    assert reaper.voteIntegral() == (tx9.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("last_unit_cost_integral", reaper.unitCostIntegral())
    print("last_unit_cost_integral_deployer", reaper.lastUnitCostIntegralFor(deployer))
    print("last_unit_cost_integral_morpheus", reaper.lastUnitCostIntegralFor(morpheus))
    print("emissionIntegral", reaper.emissionIntegral())
    print("t", tx9.timestamp)
    print("dt", tx9.timestamp - tx2.timestamp)

    # withdraw amount for deployer
    chain.mine(1, tx9.timestamp)
    tx10 = reaper.withdraw(amount, {'from': deployer})

    # wait a 2 days and check
    chain.mine(1, tx10.timestamp + 8 * day)
    tx11 = reaper.snapshot({'from': morpheus})
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx11.timestamp - tx9.timestamp) + last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == last_balances_integral
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx11.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(deployer) == last_unit_cost_integral_deployer
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral_morpheus) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 20 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 20 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.lastSnapshotTimestamp() == tx11.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx9.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx11.timestamp
    assert reaper.voteIntegral() == (tx11.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral_deployer = last_balances_integral
    last_balances_integral = reaper.balancesIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("last_unit_cost_integral", reaper.unitCostIntegral())
    print("last_unit_cost_integral_deployer", reaper.lastUnitCostIntegralFor(deployer))
    print("last_unit_cost_integral_morpheus", reaper.lastUnitCostIntegralFor(morpheus))
    print("emissionIntegral", reaper.emissionIntegral())
    print("t", tx11.timestamp)
    print("dt", tx11.timestamp - tx2.timestamp)

    # deposit for trinity 5 * amount
    chain.mine(1, tx11.timestamp)
    tx12 = reaper.deposit(5 * amount, {'from': trinity})
    assert reaper.lastUnitCostIntegralFor(trinity) == reaper.unitCostIntegral()
    last_unit_cost_integral_trinity = reaper.lastUnitCostIntegralFor(trinity)

    # wait for 15 days and check emission trinity == emission morpheus
    chain.mine(1, tx12.timestamp + 15 * day)
    tx13 = reaper.snapshot({'from': morpheus})
    chain.mine(1, tx12.timestamp + 15 * day)
    tx13 = reaper.snapshot({'from': trinity})
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == amount
    assert reaper.balances(trinity) == 5 * amount
    assert reaper.totalBalances() == 6 * amount
    assert reaper.balancesIntegral() == 6 * amount * (tx13.timestamp - tx11.timestamp) + last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == last_balances_integral_deployer
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(trinity) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx13.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(deployer) == last_unit_cost_integral_deployer
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(trinity) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus) + reaper.reapIntegralFor(trinity)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral_morpheus) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(trinity) == (reaper.lastUnitCostIntegralFor(trinity) - last_unit_cost_integral_trinity) * (5 * amount) // 2 // VOTE_DIVIDER
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 35 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(trinity) - reaper.emissionIntegral() // 2 // 35 * (15*5/6)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 35 * (10 + 15/6)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.reapIntegralFor(trinity)) <= 10 ** 8 # equal emission now
    assert reaper.lastSnapshotTimestamp() == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx9.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(trinity) == tx13.timestamp
    assert reaper.voteIntegral() == (tx13.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_balances_integral_deployer = reaper.balancesIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_unit_cost_integral_trinity = reaper.lastUnitCostIntegralFor(trinity)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)
    last_reap_integral_trinity = reaper.reapIntegralFor(trinity)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("reaper.reapIntegralFor(trinity)", reaper.reapIntegralFor(trinity))
    print("last_unit_cost_integral", reaper.unitCostIntegral())
    print("last_unit_cost_integral_deployer", reaper.lastUnitCostIntegralFor(deployer))
    print("last_unit_cost_integral_morpheus", reaper.lastUnitCostIntegralFor(morpheus))
    print("last_unit_cost_integral_trinity", reaper.lastUnitCostIntegralFor(trinity))
    print("emissionIntegral", reaper.emissionIntegral())
    print("t", tx13.timestamp)
    print("dt", tx13.timestamp - tx2.timestamp)

    # snapshot for deployer does not matter and it updates user integrals but reapIntegralFor(deployer) stays the same
    chain.mine(1, tx13.timestamp)
    tx13 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == amount
    assert reaper.balances(trinity) == 5 * amount
    assert reaper.totalBalances() == 6 * amount
    assert reaper.balancesIntegral() == last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(trinity) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == last_emission_intergal
    assert reaper.unitCostIntegral() == last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(trinity) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus) + reaper.reapIntegralFor(trinity)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == last_reap_integral_morpheus
    assert reaper.reapIntegralFor(trinity) == last_reap_integral_trinity
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 35 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(trinity) - reaper.emissionIntegral() // 2 // 35 * (15*5/6)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 35 * (10 + 15/6)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.reapIntegralFor(trinity)) <= 10 ** 8 # equal emission now
    assert reaper.lastSnapshotTimestamp() == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(trinity) == tx13.timestamp
    assert reaper.voteIntegral() == (tx13.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0

    # withdraw 4 * amount from trinity
    chain.mine(1, tx13.timestamp)
    tx13 = reaper.withdraw(4 * amount, {'from': trinity})

    # wait for day and snapshot morpheus
    chain.mine(1, tx13.timestamp + day)
    reaper.snapshot({'from': morpheus})

    # wait for 2 * day and snapshot morpheus
    chain.mine(1, tx13.timestamp + 3 * day)
    reaper.snapshot({'from': morpheus})

    # wait for 4 * day and snapshot morpheus
    chain.mine(1, tx13.timestamp + 7 * day)
    reaper.snapshot({'from': morpheus})

    # wait for 3 * day and snapshot both
    # check emission trinity == emission morpheus
    chain.mine(1, tx13.timestamp + 10 * day)
    tx14 = reaper.snapshot({'from': morpheus})
    chain.mine(1, tx13.timestamp + 10 * day)
    tx14 = reaper.snapshot({'from': trinity})
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == amount
    assert reaper.balances(trinity) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx14.timestamp - tx13.timestamp) + last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == last_balances_integral_deployer
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(trinity) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx14.timestamp - initial_emission_timestamp) // year
    assert reaper.lastUnitCostIntegralFor(deployer) == last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(trinity) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus) + reaper.reapIntegralFor(trinity)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert abs(reaper.reapIntegralFor(morpheus) - ((reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral_morpheus) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus)) <= 10
    assert reaper.reapIntegralFor(trinity) == (reaper.lastUnitCostIntegralFor(trinity) - last_unit_cost_integral_trinity) * amount // 2 // VOTE_DIVIDER + last_reap_integral_trinity
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 45 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(trinity) - reaper.emissionIntegral() // 2 // 45 * (15*5/6 + 10/2)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 45 * (10 + 15/6 + 10/2)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.reapIntegralFor(trinity)) <= 10 ** 8 # equal emission now
    assert reaper.lastSnapshotTimestamp() == tx14.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx14.timestamp
    assert reaper.lastSnapshotTimestampFor(trinity) == tx14.timestamp
    assert reaper.voteIntegral() == (tx14.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_unit_cost_integral_trinity = reaper.lastUnitCostIntegralFor(trinity)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)
    last_reap_integral_trinity = reaper.reapIntegralFor(trinity)

    print("last_emission_intergal", last_emission_intergal)
    print("last_vote_integral", last_vote_integral-init_vote_integral)
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("reaper.reapIntegralFor(trinity)", reaper.reapIntegralFor(trinity))
    print("last_unit_cost_integral", reaper.unitCostIntegral())
    print("last_unit_cost_integral_deployer", reaper.lastUnitCostIntegralFor(deployer))
    print("last_unit_cost_integral_morpheus", reaper.lastUnitCostIntegralFor(morpheus))
    print("last_unit_cost_integral_trinity", reaper.lastUnitCostIntegralFor(trinity))
    print("emissionIntegral", reaper.emissionIntegral())
    print("t", tx14.timestamp)
    print("dt", tx14.timestamp - tx2.timestamp)

    # withdraw amount for morpheus and trinity
    chain.mine(1, tx14.timestamp)
    tx15 = reaper.withdraw(amount, {'from': morpheus})
    chain.mine(1, tx14.timestamp)
    tx15 = reaper.withdraw(amount, {'from': trinity})

    # wait for 2 days and snapshot all
    # check emission has not been changed
    chain.mine(1, tx15.timestamp + 2 * day)
    tx16 = reaper.snapshot({'from': deployer})
    tx16 = reaper.snapshot({'from': morpheus})
    tx16 = reaper.snapshot({'from': trinity})
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 0
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 0
    assert reaper.balancesIntegral() == last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(trinity) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx16.timestamp - initial_emission_timestamp) // year
    assert reaper.lastUnitCostIntegralFor(deployer) == last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(morpheus) == last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(trinity) == last_unit_cost_integral
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus) + reaper.reapIntegralFor(trinity)
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == last_reap_integral_morpheus
    assert reaper.reapIntegralFor(trinity) == last_reap_integral_trinity
    assert abs(reaper.reapIntegralFor(morpheus) - ((reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral_morpheus) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus)) <= 10
    assert abs(reaper.reapIntegralFor(trinity) - ((reaper.lastUnitCostIntegralFor(trinity) - last_unit_cost_integral_trinity) * amount // 2 // VOTE_DIVIDER + last_reap_integral_trinity)) <= 10
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 47 * 10) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(trinity) - reaper.emissionIntegral() // 2 // 47 * (15*5/6 + 10/2)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.emissionIntegral() // 2 // 47 * (10 + 15/6 + 10/2)) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert abs(reaper.reapIntegralFor(morpheus) - reaper.reapIntegralFor(trinity)) <= 10 ** 8 # equal emission now
    assert reaper.lastSnapshotTimestamp() == tx16.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx16.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx16.timestamp
    assert reaper.lastSnapshotTimestampFor(trinity) == tx16.timestamp
    assert reaper.voteIntegral() == (tx16.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0

    # wait for 30 days and deposit for deployer
    chain.mine(1, tx16.timestamp + 30 * day)
    tx17 = reaper.deposit(amount, {'from': deployer})
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    
    # wait for 1 day and snapshot for deployer
    chain.mine(1, tx17.timestamp + day)
    tx18 = reaper.snapshot({'from': deployer})
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx18.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral_deployer) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    print((tx18.timestamp - initial_emission_timestamp)/86400)
    assert ((reaper.reapIntegralFor(deployer) - last_reap_integral_deployer) - (reaper.emissionIntegral() // 2 // 78)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2 // 78 * 11) <= 10 ** 8 # no boosting <=> 50% of emission, loss is about 1e-8
    assert False
