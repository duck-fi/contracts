from brownie.test import given, strategy

VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18


@given(amount=strategy('uint256', min_value=10**15, max_value=10**23))
def test_complex_boosting(lp_token, reaper, controller, voting_controller, boosting_controller_mocked, boosting_token_mocked, deployer, morpheus, trinity, MAX_UINT256, chain, year, week, day, amount):
    lp_token.transfer(morpheus, 10 * amount, {'from': deployer})
    lp_token.transfer(trinity, 10 * amount, {'from': deployer})
    initial_balance = lp_token.balanceOf(deployer)
    lp_token.approve(reaper, MAX_UINT256, {'from': deployer})
    lp_token.approve(reaper, MAX_UINT256, {'from': morpheus})
    lp_token.approve(reaper, MAX_UINT256, {'from': trinity})
    boosting_token_mocked.mint(deployer, 10**18, {'from': deployer})
    boosting_token_mocked.mint(morpheus, 10**18, {'from': deployer})
    boosting_token_mocked.approve(boosting_controller_mocked, 10**18, {'from': deployer})
    init_ts = chain.time()

    while True:
        chain.mine(1, init_ts)
        tx1 = controller.startEmission(0, {'from': deployer})
        if tx1.timestamp == init_ts:
            break
        else:
            chain.undo(1)

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
    initial_emission_timestamp = tx1.timestamp

    # deposit amount for deployer
    while True:
        chain.mine(1, init_ts)
        tx2 = reaper.deposit(amount, {'from': deployer})
        if tx2.timestamp == init_ts:
            break
        else:
            chain.undo(1)
    
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
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()

    # 1st snapshot
    while True:
        chain.mine(1, init_ts + 2 * week)
        tx3 = reaper.snapshot({'from': deployer})
        if tx3.timestamp == init_ts + 2 * week:
            break
        else:
            chain.undo(1)

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
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    print("last_reap_integral_deployer before boost",last_reap_integral_deployer)

    # boost an account on 10 week (2 week - warmup, 2 week - lock)
    while True:
        chain.mine(1, init_ts + 2 * week)
        tx4 = boosting_controller_mocked.boost(10**18, 4 * week, {'from': deployer})
        if tx4.timestamp == init_ts + 2 * week:
            break
        else:
            chain.undo(1)

    init_boost_timestamp = tx4.timestamp

    # 2nd snapshot (1 week - half of warmup)
    while True:
        chain.mine(1, init_ts + 3 * week)
        tx5 = reaper.snapshot({'from': deployer})
        if tx5.timestamp == init_ts + 3 * week:
            break
        else:
            chain.undo(1)

    print("last_reap_integral_deployer after boost",reaper.reapIntegralFor(deployer))
    print("diff",reaper.reapIntegralFor(deployer) - last_reap_integral_deployer)
    print("reaper.emissionIntegral()", reaper.emissionIntegral())
    print("reaper.boostIntegralFor(deployer)",reaper.boostIntegralFor(deployer))

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx5.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx5.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx5.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) 
    boost_koeff = (reaper.boostIntegralFor(deployer) - 0)/(10**18)/(tx5.timestamp - tx4.timestamp)
    print("boost_koeff", boost_koeff)
    emission_per_day = int(reaper.emissionIntegral() / (tx5.timestamp - initial_emission_timestamp) * 86400)
    print("emission_per_day", emission_per_day)
    assert abs(reaper.reapIntegralFor(deployer) - (int(amount // 2 + boost_koeff * amount // 2) * (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) // VOTE_DIVIDER + last_reap_integral_deployer)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(deployer) - (emission_per_day * 14 * (1/2) + emission_per_day * 7 * (1/2 + 1/2 * boost_koeff))) <= 10 ** 8 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days
    assert reaper.lastSnapshotTimestamp() == tx5.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx5.timestamp
    assert reaper.voteIntegral() == (tx5.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert abs(boost_koeff - 0.25) < 10 ** (-3)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_boost_integral_deployer = reaper.boostIntegralFor(deployer)

    # 3rd snapshot (1 week - until finish of warmup)
    while True:
        chain.mine(1, init_ts + 4 * week)
        tx6 = reaper.snapshot({'from': deployer})
        if tx6.timestamp == init_ts + 4 * week:
            break
        else:
            chain.undo(1)

    print("last_reap_integral_deployer after boost",reaper.reapIntegralFor(deployer))
    print("diff",reaper.reapIntegralFor(deployer) - last_reap_integral_deployer)
    print("reaper.emissionIntegral()", reaper.emissionIntegral())
    print("reaper.boostIntegralFor(deployer)",reaper.boostIntegralFor(deployer))

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx6.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    boost_koeff = (reaper.boostIntegralFor(deployer) - last_boost_integral_deployer)/(10**18)/(tx6.timestamp - tx5.timestamp)
    print("boost_koeff", boost_koeff)
    emission_per_day = int(reaper.emissionIntegral() / (tx6.timestamp - initial_emission_timestamp) * 86400)
    print("emission_per_day", emission_per_day)
    assert abs(reaper.reapIntegralFor(deployer) - (int(amount // 2 + boost_koeff * amount // 2) * (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) // VOTE_DIVIDER + last_reap_integral_deployer)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(deployer) - (last_reap_integral_deployer + emission_per_day * 7 * (1/2 + 1/2 * boost_koeff))) <= 10 ** 8 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days
    assert reaper.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.voteIntegral() == (tx6.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert abs(boost_koeff - 0.75) < 10 ** (-3)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_boost_integral_deployer = reaper.boostIntegralFor(deployer)

    # 4th snapshot (2 week - until finish of lock)
    while True:
        chain.mine(1, init_ts + 6 * week)
        tx7 = reaper.snapshot({'from': deployer})
        if tx7.timestamp == init_ts + 6 * week:
            break
        else:
            chain.undo(1)
    
    print("last_reap_integral_deployer after boost",reaper.reapIntegralFor(deployer))
    print("diff",reaper.reapIntegralFor(deployer) - last_reap_integral_deployer)
    print("reaper.emissionIntegral()", reaper.emissionIntegral())
    print("reaper.boostIntegralFor(deployer)",reaper.boostIntegralFor(deployer))

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx7.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx7.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx7.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    print("-----")
    print("(tx7.timestamp - tx6.timestamp)",(tx7.timestamp - tx6.timestamp))
    print("boosting_controller_mocked.boostIntegral()", boosting_controller_mocked.boostIntegral())
    print("boosting_controller_mocked.boostIntegralFor(deployer)", boosting_controller_mocked.boostIntegralFor(deployer))
    print("boosting_controller_mocked.totalBoostIntegralFor(deployer)", boosting_controller_mocked.totalBoostIntegralFor(deployer))
    print("boosting_controller_mocked.boostFactorIntegralFor(deployer)", boosting_controller_mocked.boostFactorIntegralFor(deployer))
    print("-----")
    boost_koeff = (reaper.boostIntegralFor(deployer) - last_boost_integral_deployer)/(10**18)/(tx7.timestamp - tx6.timestamp)
    print("boost_koeff", boost_koeff)
    emission_per_day = int(reaper.emissionIntegral() / (tx7.timestamp - initial_emission_timestamp) * 86400)
    print("emission_per_day", emission_per_day)
    assert abs(reaper.reapIntegralFor(deployer) - (int(amount // 2 + boost_koeff * amount // 2) * (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) // VOTE_DIVIDER + last_reap_integral_deployer)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(deployer) - (last_reap_integral_deployer + emission_per_day * 14 * (1/2 + 1/2 * boost_koeff))) <= 10 ** 8 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days
    assert reaper.lastSnapshotTimestamp() == tx7.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx7.timestamp
    assert reaper.voteIntegral() == (tx7.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert abs(boost_koeff - 1) < 10 ** (-3)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_boost_integral_deployer = reaper.boostIntegralFor(deployer)

    # 5th snapshot (2 week with no boosts)
    while True:
        chain.mine(1, init_ts + 8 * week)
        tx8 = reaper.snapshot({'from': deployer})
        if tx8.timestamp == init_ts + 8 * week:
            break
        else:
            chain.undo(1)
    
    print("last_reap_integral_deployer after boost",reaper.reapIntegralFor(deployer))
    print("diff",reaper.reapIntegralFor(deployer) - last_reap_integral_deployer)
    print("reaper.emissionIntegral()", reaper.emissionIntegral())
    print("reaper.boostIntegralFor(deployer)",reaper.boostIntegralFor(deployer))

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx8.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx8.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx8.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    print("-----")
    print("(tx7.timestamp - tx6.timestamp)",(tx8.timestamp - tx7.timestamp))
    print("boosting_controller_mocked.boostIntegral()", boosting_controller_mocked.boostIntegral())
    print("boosting_controller_mocked.boostIntegralFor(deployer)", boosting_controller_mocked.boostIntegralFor(deployer))
    print("boosting_controller_mocked.totalBoostIntegralFor(deployer)", boosting_controller_mocked.totalBoostIntegralFor(deployer))
    print("boosting_controller_mocked.boostFactorIntegralFor(deployer)", boosting_controller_mocked.boostFactorIntegralFor(deployer))
    print("-----")
    boost_koeff = (reaper.boostIntegralFor(deployer) - last_boost_integral_deployer)/(10**18)/(tx8.timestamp - tx7.timestamp)
    print("boost_koeff", boost_koeff)
    emission_per_day = int(reaper.emissionIntegral() / (tx8.timestamp - initial_emission_timestamp) * 86400)
    print("emission_per_day", emission_per_day)
    assert abs(reaper.reapIntegralFor(deployer) - (int(amount // 2 + boost_koeff * amount // 2) * (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) // VOTE_DIVIDER + last_reap_integral_deployer)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(deployer) - (last_reap_integral_deployer + emission_per_day * 14 * (1/2 + 1/2 * boost_koeff))) <= 10 ** 8 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days
    assert reaper.lastSnapshotTimestamp() == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx8.timestamp
    assert reaper.voteIntegral() == (tx8.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert abs(boost_koeff - 0) < 10 ** (-3)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_boost_integral_deployer = reaper.boostIntegralFor(deployer)

    # unboost an account
    while True:
        chain.mine(1, init_ts + 8 * week)
        tx9 = boosting_controller_mocked.unboost({'from': deployer})
        if tx9.timestamp == init_ts + 8 * week:
            break
        else:
            chain.undo(1)

    # boost an account on 8 week (2 week - warmup, 6 week - lock)
    while True:
        chain.mine(1, init_ts + 8 * week)
        tx9 = boosting_controller_mocked.boost(10**18, 8 * week, {'from': deployer})
        if tx9.timestamp == init_ts + 8 * week:
            break
        else:
            chain.undo(1)

    print("reaper.reapIntegralFor(deployer)",reaper.reapIntegralFor(deployer))
    print("reaper.unitCostIntegral()",reaper.unitCostIntegral())

    # 6th snapshot (8 week with boost + 8 week without boost)
    while True:
        chain.mine(1, init_ts + 21 * week)
        tx10 = reaper.snapshot({'from': deployer})
        if tx10.timestamp == init_ts + 21 * week:
            break
        else:
            chain.undo(1)
    
    print("last_reap_integral_deployer after boost",reaper.reapIntegralFor(deployer))
    print("diff",reaper.reapIntegralFor(deployer) - last_reap_integral_deployer)
    print("reaper.emissionIntegral()", reaper.emissionIntegral())
    print("reaper.boostIntegralFor(deployer)",reaper.boostIntegralFor(deployer))

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx10.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx10.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx10.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    print("-----")
    print("(tx7.timestamp - tx6.timestamp)",(tx10.timestamp - tx8.timestamp))
    print("boosting_controller_mocked.boostIntegral()", boosting_controller_mocked.boostIntegral())
    print("boosting_controller_mocked.boostIntegralFor(deployer)", boosting_controller_mocked.boostIntegralFor(deployer))
    print("boosting_controller_mocked.totalBoostIntegralFor(deployer)", boosting_controller_mocked.totalBoostIntegralFor(deployer))
    print("boosting_controller_mocked.boostFactorIntegralFor(deployer)", boosting_controller_mocked.boostFactorIntegralFor(deployer))
    print("-----")
    boost_koeff = (reaper.boostIntegralFor(deployer) - last_boost_integral_deployer)/(10**18)/(tx10.timestamp - tx8.timestamp)
    print("boost_koeff", boost_koeff)
    emission_per_day = int(reaper.emissionIntegral() / (tx10.timestamp - initial_emission_timestamp) * 86400)
    print("emission_per_day", emission_per_day)
    assert abs(reaper.reapIntegralFor(deployer) - (int(amount // 2 + boost_koeff * amount // 2) * (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) // VOTE_DIVIDER + last_reap_integral_deployer)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(deployer) - (last_reap_integral_deployer + emission_per_day * ((tx10.timestamp - tx8.timestamp)/day) * (1/2 + 1/2 * boost_koeff))) <= 10 ** 9 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days
    assert reaper.lastSnapshotTimestamp() == tx10.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx10.timestamp
    assert reaper.voteIntegral() == (tx10.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert abs(boost_koeff - 0.538) < 10 ** (-3)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_boost_integral_deployer = reaper.boostIntegralFor(deployer)
    last_max_emission = reaper.emissionIntegral()
    last_distributed_emission = reaper.reapIntegral()
    last_distributed_emission_deployer = reaper.reapIntegralFor(deployer)

    # now add morpheus without any boosts
    # deposit amount for morpheus
    while True:
        chain.mine(1, init_ts + 21 * week)
        tx11 = reaper.deposit(amount, {'from': morpheus})
        if tx11.timestamp == init_ts + 21 * week:
            break
        else:
            chain.undo(1)

    # wait for 2 week without boosts
    # boost an morpheus on 4 week (2 week - warmup, 2 week - lock)
    while True:
        chain.mine(1, init_ts + 23 * week)
        tx12 = boosting_controller_mocked.boost(10**18, 4 * week, {'from': morpheus})
        if tx12.timestamp == init_ts + 23 * week:
            break
        else:
            chain.undo(1)

    # wait until boost finish and for 2 week more without boosts, then resetup boost for morpheus (2 week - warmup, 4 week - lock)
    chain.mine(1, init_ts + 28 * week)
    tx12_1 = boosting_controller_mocked.unboost({'from': morpheus})

    while True:
        chain.mine(1, init_ts + 29 * week)
        tx12_2 = boosting_controller_mocked.boost(10**18, 6 * week, {'from': morpheus})
        if tx12_2.timestamp == init_ts + 29 * week:
            break
        else:
            chain.undo(1)

    # wait until boost finish and for 2 week more without boosts, then snapshot both
    while True:
        chain.mine(1, init_ts + 37 * week)
        tx13 = reaper.snapshot({'from': deployer})
        if tx13.timestamp != init_ts + 37 * week:
            chain.undo(1)
            continue
        chain.mine(1, init_ts + 37 * week)
        tx13_1 = reaper.snapshot({'from': morpheus})
        if tx13.timestamp == init_ts + 37 * week and tx13_1.timestamp == init_ts + 37 * week:
            break
        else:
            chain.undo(2)
    
    print("reaper.reapIntegralFor(deployer)",reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)",reaper.reapIntegralFor(morpheus))
    print("diff",reaper.reapIntegralFor(deployer) - last_reap_integral_deployer)
    print("reaper.emissionIntegral()", reaper.emissionIntegral())
    print("reaper.boostIntegralFor(deployer)",reaper.boostIntegralFor(deployer))

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx13.timestamp - tx10.timestamp) + last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx13.timestamp - initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(morpheus)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    print("-----")
    print("(tx7.timestamp - tx6.timestamp)",(tx13.timestamp - tx10.timestamp))
    print("boosting_controller_mocked.boostIntegral()", boosting_controller_mocked.boostIntegral())
    print("boosting_controller_mocked.boostIntegralFor(morpheus)", boosting_controller_mocked.boostIntegralFor(morpheus))
    print("boosting_controller_mocked.totalBoostIntegralFor(morpheus)", boosting_controller_mocked.totalBoostIntegralFor(morpheus))
    print("boosting_controller_mocked.boostFactorIntegralFor(morpheus)", boosting_controller_mocked.boostFactorIntegralFor(morpheus))
    print("-----")
    boost_koeff_deployer = (reaper.boostIntegralFor(deployer) - last_boost_integral_deployer)/(10**18)/(tx13.timestamp - tx10.timestamp)
    boost_koeff_morpheus = (reaper.boostIntegralFor(morpheus) - 0)/(10**18)/(tx13.timestamp - tx10.timestamp)
    print("boost_koeff_deployer", boost_koeff_deployer)
    print("boost_koeff_morpheus", boost_koeff_morpheus)
    emission_per_day = int(reaper.emissionIntegral() / (tx13.timestamp - initial_emission_timestamp) * 86400)
    print("emission_per_day", emission_per_day)
    assert abs(reaper.reapIntegralFor(deployer) - (int(amount // 2 + boost_koeff_deployer * (2*amount) // 2) * (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) // VOTE_DIVIDER + last_reap_integral_deployer)) <= 10 ** 8
    assert abs(reaper.reapIntegralFor(morpheus) - (int(amount // 2 + boost_koeff_morpheus * (2*amount) // 2) * (reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral) // VOTE_DIVIDER + 0)) <= 10 ** 8

    assert abs(reaper.reapIntegralFor(deployer) - (last_reap_integral_deployer + emission_per_day / 2 * ((tx13.timestamp - tx10.timestamp)/day) * (1/2 + 1/2 * boost_koeff_deployer))) <= 10 ** 9 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days
    assert abs(reaper.reapIntegralFor(morpheus) - (0 + emission_per_day / 2 * ((tx13.timestamp - tx10.timestamp)/day) * (1/2 + 1/2 * boost_koeff_morpheus * (2*amount)/amount))) <= 10 ** 9 # 50% of emission for 14 days, (1/2 + 1/2 * boost_koeff) for 7 days

    assert reaper.lastSnapshotTimestamp() == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx13.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx13.timestamp

    assert reaper.voteIntegral() == (tx13.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert abs(boost_koeff_deployer - 0) < 10 ** (-3)
    assert abs(boost_koeff_morpheus - 0.25) < 10 ** (-3)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)
    last_boost_integral_deployer = reaper.boostIntegralFor(deployer)
    last_boost_integral_morpheus = reaper.boostIntegralFor(morpheus)

    # check last emission distribution
    # acc_emission = emission / 2
    # deployer - 1/2 of acc_emission during 16 weeks - no boosts
    # morpheus - 1/2 of acc_emission during 6 weeks - no boosts 
    #   AND 3/4 of acc_emission during 4 weeks - 2 boost increases 
    #   AND acc_emission during 6 weeks - 2 boost max
    max_emission = reaper.emissionIntegral() - last_max_emission
    distribution_time_weeks = int((tx13.timestamp - tx10.timestamp) // 86400 // 7)
    emission_per_week_per_account = int(max_emission // distribution_time_weeks // 2)
    distributed_emission = reaper.reapIntegral() - last_distributed_emission
    distributed_emission_deployer = reaper.reapIntegralFor(deployer) - last_distributed_emission_deployer
    distributed_emission_morpheus = reaper.reapIntegralFor(morpheus)
    print(max_emission)
    print(distribution_time_weeks)
    print(emission_per_week_per_account)
    print(distributed_emission)
    print(distributed_emission_deployer)
    print(distributed_emission_morpheus)

    assert distributed_emission == distributed_emission_deployer + distributed_emission_morpheus
    # no boost 16 weeks for deployer
    assert abs(distributed_emission_deployer - (emission_per_week_per_account * distribution_time_weeks // 2)) < 10 ** 6
    # no boost 6 weeks + boost increase 4 week + max boost 6 week for morpheus
    assert abs(distributed_emission_morpheus - (emission_per_week_per_account * 6 // 2 + emission_per_week_per_account * 4 * (3/4) + emission_per_week_per_account * 6)) < 10 ** 8 
