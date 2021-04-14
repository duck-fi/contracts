from brownie.test import given, strategy

VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18


@given(amount=strategy('uint256', min_value=10**3, max_value=10**20))
def test_reaper_kill(farm_token, lp_token, controller, reaper, voting_controller, deployer, chain, year, day, exception_tester, amount):
    initial_balance = lp_token.balanceOf(deployer)
    tx = controller.startEmission(voting_controller, 0, {'from': deployer})
    initial_emission_timestamp = tx.timestamp

    chain.mine(1, chain.time() + 7 * day)

    lp_token.approve(reaper, 2 * amount, {'from': deployer})
    tx = reaper.deposit(amount, {'from': deployer})
    init_ts = tx.timestamp
    last_unit_cost_integral = reaper.unitCostIntegral()
    initial_emission_integral = reaper.emissionIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()

    while True:
        chain.mine(1, init_ts + 7 * day)
        tx1 = reaper.snapshot({'from': deployer})
        if tx1.timestamp == init_ts + 7 * day:
            break
        else:
            chain.undo(1)

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx1.timestamp - init_ts)
    assert reaper.balancesIntegralFor(
        deployer) == amount * (tx1.timestamp - init_ts)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx1.timestamp -
                                                         initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * \
        (reaper.voteIntegral() - last_vote_integral) // reaper.balancesIntegral() + \
        last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert reaper.reapIntegralFor(deployer) < reaper.emissionIntegral() // 2
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - 0) * amount // 2 // VOTE_DIVIDER
    assert reaper.lastSnapshotTimestamp() == tx1.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx1.timestamp
    assert reaper.voteIntegral() == (
        tx1.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # reap is successful
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    assert reaper.reapIntegralFor(deployer) > 0

    # kill reaper - no updates
    while True:
        chain.mine(1, init_ts + 7 * day)
        tx2 = reaper.kill({'from': deployer})
        if tx2.timestamp == init_ts + 7 * day:
            break
        else:
            chain.undo(1)

    # wait week + snapshot
    while True:
        chain.mine(1, init_ts + 14 * day)
        tx2 = reaper.snapshot({'from': deployer})
        if tx2.timestamp == init_ts + 14 * day:
            break
        else:
            chain.undo(1)

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx2.timestamp - init_ts)
    assert reaper.balancesIntegralFor(
        deployer) == amount * (tx2.timestamp - init_ts)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx2.timestamp -
                                                         initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx2.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx2.timestamp
    assert reaper.voteIntegral() == (
        tx2.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # deposit should fail
    exception_tester("reaper is killed", reaper.deposit,
                     amount, {'from': deployer})

    # wait week + snapshot + unkill reaper
    while True:
        chain.mine(1, init_ts + 21 * day)
        tx3 = reaper.snapshot({'from': deployer})
        if tx3.timestamp == init_ts + 21 * day:
            break
        else:
            chain.undo(1)
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_balances_integral = reaper.balancesIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    
    while True:
        chain.mine(1, init_ts + 21 * day)
        tx3 = reaper.unkill({'from': deployer})
        if tx3.timestamp == init_ts + 21 * day:
            break
        else:
            chain.undo(1)
    
    # wait week + snapshot
    while True:
        chain.mine(1, init_ts + 28 * day)
        tx3 = reaper.snapshot({'from': deployer})
        if tx3.timestamp == init_ts + 28 * day:
            break
        else:
            chain.undo(1)

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx3.timestamp - init_ts)
    assert reaper.balancesIntegralFor(
        deployer) == amount * (tx3.timestamp - init_ts)
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx3.timestamp -
                                                         initial_emission_timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * \
        (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + \
        last_unit_cost_integral
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert reaper.reapIntegralFor(deployer) < reaper.emissionIntegral() // 2
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - 0) * amount // 2 // VOTE_DIVIDER
    assert reaper.lastSnapshotTimestamp() == tx3.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx3.timestamp
    assert reaper.voteIntegral() == (
        tx3.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0

    assert reaper.reapIntegralFor(deployer) == ((reaper.emissionIntegral() - initial_emission_integral) // 2 // 2) # half of possible emission

    tx4 = reaper.kill({'from': deployer})

    reaper.withdraw(amount, {'from': deployer})
    assert reaper.balances(deployer) == 0
    assert reaper.totalBalances() == 0
    assert initial_balance == lp_token.balanceOf(deployer)
