from brownie.test import given, strategy

VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18
INIT_VOTING_TIME = 1_609_372_800


@given(amount=strategy('uint256', min_value=10**3, max_value=10**23))
def test_complex_voting(farm_token, lp_token, controller, reaper, reaper_2, reaper_3, voting_controller, deployer, morpheus, trinity, thomas, MAX_UINT256, chain, year, week, day, amount):
    lp_token.transfer(morpheus, 10 * amount, {'from': deployer})
    lp_token.transfer(trinity, 10 * amount, {'from': deployer})
    lp_token.transfer(thomas, 10 * amount, {'from': deployer})
    initial_balance = lp_token.balanceOf(deployer)
    lp_token.approve(reaper, MAX_UINT256, {'from': deployer})
    lp_token.approve(reaper, MAX_UINT256, {'from': morpheus})
    lp_token.approve(reaper, MAX_UINT256, {'from': trinity})
    lp_token.approve(reaper, MAX_UINT256, {'from': thomas})
    lp_token.approve(reaper_2, MAX_UINT256, {'from': deployer})
    lp_token.approve(reaper_2, MAX_UINT256, {'from': morpheus})
    lp_token.approve(reaper_2, MAX_UINT256, {'from': trinity})
    lp_token.approve(reaper_2, MAX_UINT256, {'from': thomas})
    lp_token.approve(reaper_3, MAX_UINT256, {'from': deployer})
    lp_token.approve(reaper_3, MAX_UINT256, {'from': morpheus})
    lp_token.approve(reaper_3, MAX_UINT256, {'from': trinity})
    lp_token.approve(reaper_3, MAX_UINT256, {'from': thomas})
    farm_token.approve(voting_controller, MAX_UINT256, {'from': deployer})
    init_ts = chain.time()

    # deposit on reaper
    while True:
        chain.mine(1, init_ts + day)
        tx1 = reaper.deposit(amount, {'from': deployer})
        chain.mine(1, init_ts + day)
        tx1_2 = reaper_2.deposit(amount, {'from': deployer})
        if tx1.timestamp == tx1_2.timestamp:
            break
        else:
            chain.undo(2)

    # deposit on reaper_2
    while True:
        chain.mine(1, init_ts + 2 * day)
        tx2 = reaper.deposit(amount, {'from': morpheus})
        chain.mine(1, init_ts + 2 * day)
        tx2_1 = reaper_2.deposit(amount, {'from': morpheus})
        if tx2.timestamp == tx2_1.timestamp:
            break
        else:
            chain.undo(2)

    # try to make a snapshot now (zero integrals)
    while True:
        chain.mine(1, init_ts + 3 * day)
        tx3 = reaper.snapshot({'from': deployer})
        chain.mine(1, init_ts + 3 * day)
        tx3_1 = reaper.snapshot({'from': morpheus})
        if tx3.timestamp == tx3_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 0
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == 0
    assert reaper.unitCostIntegral() == 0
    assert reaper.lastUnitCostIntegralFor(deployer) == 0
    assert reaper.lastUnitCostIntegralFor(morpheus) == 0
    assert reaper.reapIntegral() == 0
    assert reaper.reapIntegralFor(deployer) == 0
    assert reaper.reapIntegralFor(morpheus) == 0
    assert reaper.lastSnapshotTimestamp() == tx3.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx3.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx3.timestamp
    assert reaper.voteIntegral() == 0
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()

    # set init vote share # TODO: here is a bug if no votes for period => integral has not been updated => if vote share reducing ==> crash
    # TODO: remove TODO: add one more test
    # voting_controller.vote(reaper, farm_token, 1, {'from': deployer})
    # voting_controller.vote(reaper_2, farm_token, 1, {'from': deployer})

    # wait for 7 days
    # startVoting + startEmission
    aligned_time = INIT_VOTING_TIME + \
        ((chain.time() + week - INIT_VOTING_TIME) // week) * week + 1
    while True:
        chain.mine(1, aligned_time)
        tx_emission = controller.startEmission(
            voting_controller, 0, {'from': deployer})
        if tx_emission.timestamp == aligned_time:
            break
        else:
            chain.undo(2)

    # 1st snapshot for both on reaper after 1 day
    while True:
        chain.mine(1, aligned_time + 1 * day)
        tx4 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 1 * day)
        tx4_1 = reaper.snapshot({'from': morpheus})
        if tx4.timestamp == tx4_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx4.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx4.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * \
        (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - 0)
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() //
               4) <= 10 ** 8  # reaper share=50%, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx4.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx4.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx4.timestamp
    assert reaper.voteIntegral() == (tx4.timestamp - tx_emission.timestamp) * \
        VOTE_DIVIDER // 2  # reaper share=50%
    assert reaper.voteIntegral() / (tx4.timestamp - tx_emission.timestamp) / \
        VOTE_DIVIDER == 0.5
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    print(reaper.emissionIntegral())
    print(reaper.voteIntegral())
    print(reaper.balancesIntegral())
    print(reaper.unitCostIntegral())
    print(reaper.reapIntegral())
    print(reaper.reapIntegralFor(deployer))
    print(reaper.reapIntegralFor(morpheus))
    print(reaper.emissionIntegral()/reaper.reapIntegral())

    # modify vote share
    voting_controller.vote(reaper, farm_token, 1, {
                           'from': deployer})  # TODO: fix
    voting_controller.vote(reaper_2, farm_token, 3, {
                           'from': deployer})  # TODO: 3

    # wait till next voting period
    chain.mine(1, aligned_time + week)
    voting_controller.snapshot()  # need to do in case no reaper.snapshot in this week

    # 2nd snapshot for both on reaper (see reduction)
    while True:
        chain.mine(1, aligned_time + 2 * week)
        tx5 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 2 * week)
        tx5_1 = reaper.snapshot({'from': morpheus})
        if tx5.timestamp == tx5_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx5.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx5.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx5.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx5.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx5.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx5.timestamp
    assert abs(reaper.voteIntegral() / (tx5.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.375) < 10 ** (-6)
    assert voting_controller.lastVotes(reaper) == 0.25 * 10 ** 18
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # modify vote share
    voting_controller.vote(reaper, farm_token, 1, {'from': deployer})
    voting_controller.unvote(reaper_2, farm_token, 1, {'from': deployer})

    # wait till next voting period + some time
    chain.mine(1, aligned_time + 3 * week)
    # voting_controller.snapshot() # need to do in case no reaper.snapshot in this week

    # 3rd snapshot for both on reaper (see reduction and check voteIntegral)
    while True:
        chain.mine(1, aligned_time + 3 * week + 100)
        tx6 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 3 * week + 100)
        tx6_1 = reaper.snapshot({'from': morpheus})
        if tx6.timestamp == tx6_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx6.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx6.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx6.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx6.timestamp
    assert abs(reaper.voteIntegral() / (tx6.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.333) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 0.5 * 10 ** 18
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # wait time in current voting period
    while True:
        chain.mine(1, aligned_time + 3 * week + week/2)
        tx6 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 3 * week + week/2)
        tx6_1 = reaper.snapshot({'from': morpheus})
        if tx6.timestamp == tx6_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx6.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx6.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx6.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx6.timestamp
    assert abs(reaper.voteIntegral() / (tx6.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.357) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 0.5 * 10 ** 18
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # wait time in current voting period
    while True:
        chain.mine(1, aligned_time + 3 * week + week - 100)
        tx6 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 3 * week + week - 100)
        tx6_1 = reaper.snapshot({'from': morpheus})
        if tx6.timestamp == tx6_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx6.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx6.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx6.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx6.timestamp
    assert abs(reaper.voteIntegral() / (tx6.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.375) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 0.5 * 10 ** 18
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # snapshot on reaper_2
    while True:
        chain.mine(1, aligned_time + 3 * week + week - 100)
        tx6 = reaper_2.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 3 * week + week - 100)
        tx6_1 = reaper_2.snapshot({'from': morpheus})
        if tx6.timestamp == tx6_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_2.balances(deployer) == amount
    assert reaper_2.balances(morpheus) == amount
    assert reaper_2.totalBalances() == 2 * amount
    assert reaper_2.balancesIntegral() == 2 * amount * \
        (tx6.timestamp - tx_emission.timestamp)
    assert reaper_2.balancesIntegralFor(
        deployer) == reaper_2.balancesIntegral()
    assert reaper_2.balancesIntegralFor(
        morpheus) == reaper_2.balancesIntegral()
    assert reaper_2.emissionIntegral() == YEAR_EMISSION * \
        (tx6.timestamp - tx_emission.timestamp) // year
    assert reaper_2.unitCostIntegral() == (reaper_2.emissionIntegral() - 0) * \
        (reaper_2.voteIntegral() - 0) // (reaper_2.balancesIntegral() - 0) + 0
    assert reaper_2.lastUnitCostIntegralFor(
        deployer) == reaper_2.unitCostIntegral()
    assert reaper_2.lastUnitCostIntegralFor(
        morpheus) == reaper_2.unitCostIntegral()
    assert reaper_2.reapIntegral() == reaper_2.reapIntegralFor(
        deployer) + reaper_2.reapIntegralFor(morpheus)
    voting_koeff_2 = reaper_2.voteIntegral() / (tx6.timestamp -
                                                tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff_2)
    assert abs(reaper_2.reapIntegral() - reaper_2.emissionIntegral() // 2 *
               voting_koeff_2) <= 10 ** 8  # reaper_2 share=voting_koeff_2, no boosts
    assert reaper_2.reapIntegralFor(deployer) == (
        reaper_2.lastUnitCostIntegralFor(deployer) - 0) * amount // 2 // VOTE_DIVIDER + 0
    assert reaper_2.reapIntegralFor(morpheus) == (
        reaper_2.lastUnitCostIntegralFor(morpheus) - 0) * amount // 2 // VOTE_DIVIDER + 0
    assert reaper_2.reapIntegralFor(
        deployer) == reaper_2.reapIntegralFor(morpheus)
    assert reaper_2.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper_2.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper_2.lastSnapshotTimestampFor(morpheus) == tx6.timestamp
    assert abs(reaper_2.voteIntegral() / (tx6.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.625) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_2) == 0.5 * 10 ** 18
    assert reaper_2.boostIntegralFor(deployer) == 0
    assert reaper_2.totalBoostIntegralFor(deployer) == 0
    assert reaper_2.boostIntegralFor(morpheus) == 0
    assert reaper_2.totalBoostIntegralFor(morpheus) == 0
    last_reaper_2_balances_integral = reaper_2.balancesIntegral()
    last_reaper_2_emission_integral = reaper_2.emissionIntegral()
    last_reaper_2_vote_integral = reaper_2.voteIntegral()
    last_reaper_2_unit_cost_integral = reaper_2.unitCostIntegral()
    last_reaper_2_reap_integral_deployer = reaper_2.reapIntegralFor(deployer)
    last_reaper_2_reap_integral_morpheus = reaper_2.reapIntegralFor(morpheus)

    # compare voting and emission
    assert abs(reaper_2.reapIntegral() + reaper.reapIntegral() -
               reaper_2.emissionIntegral() // 2) < 10 ** 8
    assert abs(voting_koeff + voting_koeff_2 - 1) < 10 ** (-3)

    # add new reaper (reaper_3)
    controller.addReaper(reaper_3)

    # deposit on reaper_3
    while True:
        chain.mine(1, aligned_time + 3 * week + week - 100)
        tx7 = reaper_3.deposit(amount, {'from': deployer})
        chain.mine(1, aligned_time + 3 * week + week - 100)
        tx7_1 = reaper_3.deposit(amount, {'from': morpheus})
        if tx7.timestamp == tx7_1.timestamp:
            break
        else:
            chain.undo(2)

    init_reaper_3_emission_integral = reaper_3.emissionIntegral()
    previous_emission_integral = reaper_3.emissionIntegral()
    reaper_3_init_timestamp = tx7

    # modify vote share
    voting_controller.vote(reaper_3, farm_token, 2, {'from': deployer})

    # wait till next voting period
    chain.mine(1, aligned_time + 4 * week)

    # snapshot reaper
    while True:
        chain.mine(1, aligned_time + 4 * week + week - 100)
        tx8 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 4 * week + week - 100)
        tx8_1 = reaper.snapshot({'from': morpheus})
        if tx8.timestamp == tx8_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx8.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx8.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx8.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    distributed_emission_reaper = (reaper.unitCostIntegral(
    ) - last_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx8.timestamp
    assert abs(reaper.voteIntegral() / (tx8.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.366) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 333333333333333333
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # snapshot reaper_2 (check that reaper_2 got correct value)
    while True:
        chain.mine(1, aligned_time + 4 * week + week - 100)
        tx9 = reaper_2.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 4 * week + week - 100)
        tx9_1 = reaper_2.snapshot({'from': morpheus})
        if tx9.timestamp == tx9_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_2.balances(deployer) == amount
    assert reaper_2.balances(morpheus) == amount
    assert reaper_2.totalBalances() == 2 * amount
    assert reaper_2.balancesIntegral() == 2 * amount * \
        (tx9.timestamp - tx_emission.timestamp)
    assert reaper_2.balancesIntegralFor(
        deployer) == reaper_2.balancesIntegral()
    assert reaper_2.balancesIntegralFor(
        morpheus) == reaper_2.balancesIntegral()
    assert reaper_2.emissionIntegral() == YEAR_EMISSION * \
        (tx9.timestamp - tx_emission.timestamp) // year
    assert reaper_2.unitCostIntegral() == (reaper_2.emissionIntegral() - last_reaper_2_emission_integral) * (reaper_2.voteIntegral() -
                                                                                                             last_reaper_2_vote_integral) // (reaper_2.balancesIntegral() - last_reaper_2_balances_integral) + last_reaper_2_unit_cost_integral
    assert reaper_2.lastUnitCostIntegralFor(
        deployer) == reaper_2.unitCostIntegral()
    assert reaper_2.lastUnitCostIntegralFor(
        morpheus) == reaper_2.unitCostIntegral()
    assert reaper_2.reapIntegral() == reaper_2.reapIntegralFor(
        deployer) + reaper_2.reapIntegralFor(morpheus)
    voting_koeff_2 = reaper_2.voteIntegral() / (tx9.timestamp -
                                                tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff_2)
    assert abs(reaper_2.reapIntegral() - reaper_2.emissionIntegral() // 2 *
               voting_koeff_2) <= 10 ** 8  # reaper_2 share=voting_koeff_2, no boosts
    distributed_emission_reaper_2 = (reaper_2.unitCostIntegral(
    ) - last_reaper_2_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_2.reapIntegralFor(deployer) == (reaper_2.lastUnitCostIntegralFor(
        deployer) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(morpheus) == (reaper_2.lastUnitCostIntegralFor(
        morpheus) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_morpheus
    assert reaper_2.reapIntegralFor(
        deployer) == reaper_2.reapIntegralFor(morpheus)
    assert reaper_2.lastSnapshotTimestamp() == tx9.timestamp
    assert reaper_2.lastSnapshotTimestampFor(deployer) == tx9.timestamp
    assert reaper_2.lastSnapshotTimestampFor(morpheus) == tx9.timestamp
    assert abs(reaper_2.voteIntegral() / (tx9.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.566) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_2) == 333333333333333333
    assert reaper_2.boostIntegralFor(deployer) == 0
    assert reaper_2.totalBoostIntegralFor(deployer) == 0
    assert reaper_2.boostIntegralFor(morpheus) == 0
    assert reaper_2.totalBoostIntegralFor(morpheus) == 0
    last_reaper_2_balances_integral = reaper_2.balancesIntegral()
    last_reaper_2_emission_integral = reaper_2.emissionIntegral()
    last_reaper_2_vote_integral = reaper_2.voteIntegral()
    last_reaper_2_unit_cost_integral = reaper_2.unitCostIntegral()
    last_reaper_2_reap_integral_deployer = reaper_2.reapIntegralFor(deployer)
    last_reaper_2_reap_integral_morpheus = reaper_2.reapIntegralFor(morpheus)

    # snapshot reaper_3 (check that reaper_3 got correct value)
    while True:
        chain.mine(1, aligned_time + 4 * week + week - 100)
        tx10 = reaper_3.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 4 * week + week - 100)
        tx10_1 = reaper_3.snapshot({'from': morpheus})
        if tx10.timestamp == tx10_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_3.balances(deployer) == amount
    assert reaper_3.balances(morpheus) == amount
    assert reaper_3.totalBalances() == 2 * amount
    assert reaper_3.balancesIntegral() == 2 * amount * \
        (tx10.timestamp - tx7.timestamp)
    assert reaper_3.balancesIntegralFor(
        deployer) == reaper_3.balancesIntegral()
    assert reaper_3.balancesIntegralFor(
        morpheus) == reaper_3.balancesIntegral()
    assert reaper_3.emissionIntegral() == YEAR_EMISSION * \
        (tx10.timestamp - tx_emission.timestamp) // year
    assert reaper_3.unitCostIntegral() == (reaper_3.emissionIntegral() - init_reaper_3_emission_integral) * \
        (reaper_3.voteIntegral() - 0) // (reaper_3.balancesIntegral() - 0) + 0
    assert reaper_3.lastUnitCostIntegralFor(
        deployer) == reaper_3.unitCostIntegral()
    assert reaper_3.lastUnitCostIntegralFor(
        morpheus) == reaper_3.unitCostIntegral()
    assert reaper_3.reapIntegral() == reaper_3.reapIntegralFor(
        deployer) + reaper_3.reapIntegralFor(morpheus)
    voting_koeff_3 = reaper_3.voteIntegral() / (tx10.timestamp -
                                                reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER
    print(voting_koeff_3)
    assert abs(reaper_3.reapIntegral() - (reaper_3.emissionIntegral() - init_reaper_3_emission_integral) //
               2 * voting_koeff_3) <= 10 ** 8  # reaper_3 share=voting_koeff_3, no boosts
    distributed_emission_reaper_3 = (
        reaper_3.unitCostIntegral() - 0) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_3.reapIntegralFor(deployer) == (
        reaper_3.lastUnitCostIntegralFor(deployer) - 0) * amount // 2 // VOTE_DIVIDER + 0
    assert reaper_3.reapIntegralFor(morpheus) == (
        reaper_3.lastUnitCostIntegralFor(morpheus) - 0) * amount // 2 // VOTE_DIVIDER + 0
    assert reaper_3.reapIntegralFor(
        deployer) == reaper_3.reapIntegralFor(morpheus)
    assert reaper_3.lastSnapshotTimestamp() == tx10.timestamp
    assert reaper_3.lastSnapshotTimestampFor(deployer) == tx10.timestamp
    assert reaper_3.lastSnapshotTimestampFor(morpheus) == tx10.timestamp
    voting_koeff_3_full = reaper_3.voteIntegral(
    ) / (tx10.timestamp - tx_emission.timestamp) / VOTE_DIVIDER
    assert abs(reaper_3.voteIntegral() / (tx10.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.066) < 10 ** (-3)
    assert abs(reaper_3.voteIntegral() / (tx10.timestamp -
               reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER - 0.333) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_3) == 333333333333333333
    assert reaper_3.boostIntegralFor(deployer) == 0
    assert reaper_3.totalBoostIntegralFor(deployer) == 0
    assert reaper_3.boostIntegralFor(morpheus) == 0
    assert reaper_3.totalBoostIntegralFor(morpheus) == 0
    last_reaper_3_balances_integral = reaper_3.balancesIntegral()
    last_reaper_3_emission_integral = reaper_3.emissionIntegral()
    last_reaper_3_vote_integral = reaper_3.voteIntegral()
    last_reaper_3_unit_cost_integral = reaper_3.unitCostIntegral()
    last_reaper_3_reap_integral_deployer = reaper_3.reapIntegralFor(deployer)
    last_reaper_3_reap_integral_morpheus = reaper_3.reapIntegralFor(morpheus)

    # check emission share
    distributed_emission = (reaper_3.emissionIntegral() -
                            previous_emission_integral) // 2
    previous_emission_integral = reaper_3.emissionIntegral()
    print("--------")
    print(distributed_emission, "distributed_emission")
    print(distributed_emission_reaper, "distributed_emission_reaper")
    print(distributed_emission_reaper_2, "distributed_emission_reaper_2")
    print(distributed_emission_reaper_3, "distributed_emission_reaper_3")
    print("--------")
    assert abs(distributed_emission - distributed_emission_reaper -
               distributed_emission_reaper_2 - distributed_emission_reaper_3) < 10 ** 8
    assert abs(voting_koeff + voting_koeff_2 +
               voting_koeff_3_full - 1) < 10 ** (-3)

    # modify vote share
    voting_controller.vote(reaper_3, farm_token, 2, {'from': deployer})

    # wait till next voting period
    chain.mine(1, aligned_time + 5 * week)

    # snapshot reaper
    while True:
        chain.mine(1, aligned_time + 5 * week + week - 10)
        tx11 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 5 * week + week - 10)
        tx11_1 = reaper.snapshot({'from': morpheus})
        if tx11.timestamp == tx11_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx11.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx11.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx11.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    distributed_emission_reaper = (reaper.unitCostIntegral(
    ) - last_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx11.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx11.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx11.timestamp
    assert abs(reaper.voteIntegral() / (tx11.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.347) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 250000000000000000
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # snapshot reaper_2 (check that reaper_2 got correct value)
    while True:
        chain.mine(1, aligned_time + 5 * week + week - 10)
        tx12 = reaper_2.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 5 * week + week - 10)
        tx12_1 = reaper_2.snapshot({'from': morpheus})
        if tx12.timestamp == tx12_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_2.balances(deployer) == amount
    assert reaper_2.balances(morpheus) == amount
    assert reaper_2.totalBalances() == 2 * amount
    assert reaper_2.balancesIntegral() == 2 * amount * \
        (tx12.timestamp - tx_emission.timestamp)
    assert reaper_2.balancesIntegralFor(
        deployer) == reaper_2.balancesIntegral()
    assert reaper_2.balancesIntegralFor(
        morpheus) == reaper_2.balancesIntegral()
    assert reaper_2.emissionIntegral() == YEAR_EMISSION * \
        (tx12.timestamp - tx_emission.timestamp) // year
    assert reaper_2.unitCostIntegral() == (reaper_2.emissionIntegral() - last_reaper_2_emission_integral) * (reaper_2.voteIntegral() -
                                                                                                             last_reaper_2_vote_integral) // (reaper_2.balancesIntegral() - last_reaper_2_balances_integral) + last_reaper_2_unit_cost_integral
    assert reaper_2.lastUnitCostIntegralFor(
        deployer) == reaper_2.unitCostIntegral()
    assert reaper_2.lastUnitCostIntegralFor(
        morpheus) == reaper_2.unitCostIntegral()
    assert reaper_2.reapIntegral() == reaper_2.reapIntegralFor(
        deployer) + reaper_2.reapIntegralFor(morpheus)
    voting_koeff_2 = reaper_2.voteIntegral() / (tx12.timestamp -
                                                tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff_2)
    assert abs(reaper_2.reapIntegral() - reaper_2.emissionIntegral() // 2 *
               voting_koeff_2) <= 10 ** 8  # reaper_2 share=voting_koeff_2, no boosts
    distributed_emission_reaper_2 = (reaper_2.unitCostIntegral(
    ) - last_reaper_2_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_2.reapIntegralFor(deployer) == (reaper_2.lastUnitCostIntegralFor(
        deployer) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(morpheus) == (reaper_2.lastUnitCostIntegralFor(
        morpheus) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(
        deployer) == reaper_2.reapIntegralFor(morpheus)
    assert reaper_2.lastSnapshotTimestamp() == tx12.timestamp
    assert reaper_2.lastSnapshotTimestampFor(deployer) == tx12.timestamp
    assert reaper_2.lastSnapshotTimestampFor(morpheus) == tx12.timestamp
    assert abs(reaper_2.voteIntegral() / (tx12.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.513) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_2) == 250000000000000000
    assert reaper_2.boostIntegralFor(deployer) == 0
    assert reaper_2.totalBoostIntegralFor(deployer) == 0
    assert reaper_2.boostIntegralFor(morpheus) == 0
    assert reaper_2.totalBoostIntegralFor(morpheus) == 0
    last_reaper_2_balances_integral = reaper_2.balancesIntegral()
    last_reaper_2_emission_integral = reaper_2.emissionIntegral()
    last_reaper_2_vote_integral = reaper_2.voteIntegral()
    last_reaper_2_unit_cost_integral = reaper_2.unitCostIntegral()
    last_reaper_2_reap_integral_deployer = reaper_2.reapIntegralFor(deployer)
    last_reaper_2_reap_integral_morpheus = reaper_2.reapIntegralFor(morpheus)

    # snapshot reaper_3 (check that reaper_3 got correct value)
    while True:
        chain.mine(1, aligned_time + 5 * week + week - 10)
        tx13 = reaper_3.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 5 * week + week - 10)
        tx13_1 = reaper_3.snapshot({'from': morpheus})
        if tx13.timestamp == tx13_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_3.balances(deployer) == amount
    assert reaper_3.balances(morpheus) == amount
    assert reaper_3.totalBalances() == 2 * amount
    assert reaper_3.balancesIntegral() == 2 * amount * \
        (tx13.timestamp - tx7.timestamp)
    assert reaper_3.balancesIntegralFor(
        deployer) == reaper_3.balancesIntegral()
    assert reaper_3.balancesIntegralFor(
        morpheus) == reaper_3.balancesIntegral()
    assert reaper_3.emissionIntegral() == YEAR_EMISSION * \
        (tx13.timestamp - tx_emission.timestamp) // year
    assert reaper_3.unitCostIntegral() == (reaper_3.emissionIntegral() - last_reaper_3_emission_integral) * (reaper_3.voteIntegral() -
                                                                                                             last_reaper_3_vote_integral) // (reaper_3.balancesIntegral() - last_reaper_3_balances_integral) + last_reaper_3_unit_cost_integral
    assert reaper_3.lastUnitCostIntegralFor(
        deployer) == reaper_3.unitCostIntegral()
    assert reaper_3.lastUnitCostIntegralFor(
        morpheus) == reaper_3.unitCostIntegral()
    assert reaper_3.reapIntegral() == reaper_3.reapIntegralFor(
        deployer) + reaper_3.reapIntegralFor(morpheus)
    voting_koeff_3 = reaper_3.voteIntegral() / (tx13.timestamp -
                                                reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER
    print(voting_koeff_3)
    assert abs(reaper_3.reapIntegral() - (reaper_3.emissionIntegral() - init_reaper_3_emission_integral) //
               2 * voting_koeff_3) <= 10 ** 8  # reaper_3 share=voting_koeff_3, no boosts
    distributed_emission_reaper_3 = (reaper_3.unitCostIntegral(
    ) - last_reaper_3_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_3.reapIntegralFor(deployer) == (reaper_3.lastUnitCostIntegralFor(
        deployer) - last_reaper_3_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_3_reap_integral_deployer
    assert reaper_3.reapIntegralFor(morpheus) == (reaper_3.lastUnitCostIntegralFor(
        morpheus) - last_reaper_3_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_3_reap_integral_deployer
    assert reaper_3.reapIntegralFor(
        deployer) == reaper_3.reapIntegralFor(morpheus)
    assert reaper_3.lastSnapshotTimestamp() == tx13.timestamp
    assert reaper_3.lastSnapshotTimestampFor(deployer) == tx13.timestamp
    assert reaper_3.lastSnapshotTimestampFor(morpheus) == tx13.timestamp
    voting_koeff_3_full = reaper_3.voteIntegral(
    ) / (tx13.timestamp - tx_emission.timestamp) / VOTE_DIVIDER
    assert abs(reaper_3.voteIntegral() / (tx13.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.138) < 10 ** (-3)
    assert abs(reaper_3.voteIntegral() / (tx13.timestamp -
               reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER - 0.416) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_3) == 0.5 * 10 ** 18
    assert reaper_3.boostIntegralFor(deployer) == 0
    assert reaper_3.totalBoostIntegralFor(deployer) == 0
    assert reaper_3.boostIntegralFor(morpheus) == 0
    assert reaper_3.totalBoostIntegralFor(morpheus) == 0
    last_reaper_3_balances_integral = reaper_3.balancesIntegral()
    last_reaper_3_emission_integral = reaper_3.emissionIntegral()
    last_reaper_3_vote_integral = reaper_3.voteIntegral()
    last_reaper_3_unit_cost_integral = reaper_3.unitCostIntegral()
    last_reaper_3_reap_integral_deployer = reaper_3.reapIntegralFor(deployer)
    last_reaper_3_reap_integral_morpheus = reaper_3.reapIntegralFor(morpheus)

    # check emission share
    distributed_emission = (reaper_3.emissionIntegral() -
                            previous_emission_integral) // 2
    previous_emission_integral = reaper_3.emissionIntegral()
    print("--------")
    print(distributed_emission, "distributed_emission")
    print(distributed_emission_reaper, "distributed_emission_reaper")
    print(distributed_emission_reaper_2, "distributed_emission_reaper_2")
    print(distributed_emission_reaper_3, "distributed_emission_reaper_3")
    print("--------")
    assert abs(distributed_emission - distributed_emission_reaper -
               distributed_emission_reaper_2 - distributed_emission_reaper_3) < 10 ** 8
    assert abs(voting_koeff + voting_koeff_2 +
               voting_koeff_3_full - 1) < 10 ** (-3)

    # modify vote share (set zero share for reaper_3)
    voting_controller.unvote(reaper_3, farm_token, 4, {'from': deployer})

    # wait till next voting period
    chain.mine(1, aligned_time + 6 * week)

    # snapshot reaper
    while True:
        chain.mine(1, aligned_time + 6 * week + week - 10)
        tx14 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 6 * week + week - 10)
        tx14_1 = reaper.snapshot({'from': morpheus})
        if tx14.timestamp == tx14_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx14.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx14.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx14.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    distributed_emission_reaper = (reaper.unitCostIntegral(
    ) - last_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx14.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx14.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx14.timestamp
    assert abs(reaper.voteIntegral() / (tx14.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.369) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 500000000000000000
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # snapshot reaper_2 (check that reaper_2 got correct value)
    while True:
        chain.mine(1, aligned_time + 6 * week + week - 10)
        tx15 = reaper_2.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 6 * week + week - 10)
        tx15_1 = reaper_2.snapshot({'from': morpheus})
        if tx15.timestamp == tx15_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_2.balances(deployer) == amount
    assert reaper_2.balances(morpheus) == amount
    assert reaper_2.totalBalances() == 2 * amount
    assert reaper_2.balancesIntegral() == 2 * amount * \
        (tx15.timestamp - tx_emission.timestamp)
    assert reaper_2.balancesIntegralFor(
        deployer) == reaper_2.balancesIntegral()
    assert reaper_2.balancesIntegralFor(
        morpheus) == reaper_2.balancesIntegral()
    assert reaper_2.emissionIntegral() == YEAR_EMISSION * \
        (tx15.timestamp - tx_emission.timestamp) // year
    assert reaper_2.unitCostIntegral() == (reaper_2.emissionIntegral() - last_reaper_2_emission_integral) * (reaper_2.voteIntegral() -
                                                                                                             last_reaper_2_vote_integral) // (reaper_2.balancesIntegral() - last_reaper_2_balances_integral) + last_reaper_2_unit_cost_integral
    assert reaper_2.lastUnitCostIntegralFor(
        deployer) == reaper_2.unitCostIntegral()
    assert reaper_2.lastUnitCostIntegralFor(
        morpheus) == reaper_2.unitCostIntegral()
    assert reaper_2.reapIntegral() == reaper_2.reapIntegralFor(
        deployer) + reaper_2.reapIntegralFor(morpheus)
    voting_koeff_2 = reaper_2.voteIntegral() / (tx15.timestamp -
                                                tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff_2)
    assert abs(reaper_2.reapIntegral() - reaper_2.emissionIntegral() // 2 *
               voting_koeff_2) <= 10 ** 8  # reaper_2 share=voting_koeff_2, no boosts
    distributed_emission_reaper_2 = (reaper_2.unitCostIntegral(
    ) - last_reaper_2_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_2.reapIntegralFor(deployer) == (reaper_2.lastUnitCostIntegralFor(
        deployer) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(morpheus) == (reaper_2.lastUnitCostIntegralFor(
        morpheus) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(
        deployer) == reaper_2.reapIntegralFor(morpheus)
    assert reaper_2.lastSnapshotTimestamp() == tx15.timestamp
    assert reaper_2.lastSnapshotTimestampFor(deployer) == tx15.timestamp
    assert reaper_2.lastSnapshotTimestampFor(morpheus) == tx15.timestamp
    assert abs(reaper_2.voteIntegral() / (tx15.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.511) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_2) == 500000000000000000
    assert reaper_2.boostIntegralFor(deployer) == 0
    assert reaper_2.totalBoostIntegralFor(deployer) == 0
    assert reaper_2.boostIntegralFor(morpheus) == 0
    assert reaper_2.totalBoostIntegralFor(morpheus) == 0
    last_reaper_2_balances_integral = reaper_2.balancesIntegral()
    last_reaper_2_emission_integral = reaper_2.emissionIntegral()
    last_reaper_2_vote_integral = reaper_2.voteIntegral()
    last_reaper_2_unit_cost_integral = reaper_2.unitCostIntegral()
    last_reaper_2_reap_integral_deployer = reaper_2.reapIntegralFor(deployer)
    last_reaper_2_reap_integral_morpheus = reaper_2.reapIntegralFor(morpheus)

    # snapshot reaper_3 (check that reaper_3 got correct value)
    while True:
        chain.mine(1, aligned_time + 6 * week + week - 10)
        tx16 = reaper_3.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 6 * week + week - 10)
        tx16_1 = reaper_3.snapshot({'from': morpheus})
        if tx16.timestamp == tx16_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_3.balances(deployer) == amount
    assert reaper_3.balances(morpheus) == amount
    assert reaper_3.totalBalances() == 2 * amount
    assert reaper_3.balancesIntegral() == 2 * amount * \
        (tx16.timestamp - tx7.timestamp)
    assert reaper_3.balancesIntegralFor(
        deployer) == reaper_3.balancesIntegral()
    assert reaper_3.balancesIntegralFor(
        morpheus) == reaper_3.balancesIntegral()
    assert reaper_3.emissionIntegral() == YEAR_EMISSION * \
        (tx16.timestamp - tx_emission.timestamp) // year
    assert reaper_3.unitCostIntegral() == (reaper_3.emissionIntegral() - last_reaper_3_emission_integral) * (reaper_3.voteIntegral() -
                                                                                                             last_reaper_3_vote_integral) // (reaper_3.balancesIntegral() - last_reaper_3_balances_integral) + last_reaper_3_unit_cost_integral
    assert reaper_3.lastUnitCostIntegralFor(
        deployer) == reaper_3.unitCostIntegral()
    assert reaper_3.lastUnitCostIntegralFor(
        morpheus) == reaper_3.unitCostIntegral()
    assert reaper_3.reapIntegral() == reaper_3.reapIntegralFor(
        deployer) + reaper_3.reapIntegralFor(morpheus)
    voting_koeff_3 = reaper_3.voteIntegral() / (tx16.timestamp -
                                                reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER
    print(voting_koeff_3)
    assert abs(reaper_3.reapIntegral() - (reaper_3.emissionIntegral() - init_reaper_3_emission_integral) //
               2 * voting_koeff_3) <= 10 ** 8  # reaper_3 share=voting_koeff_3, no boosts
    distributed_emission_reaper_3 = (reaper_3.unitCostIntegral(
    ) - last_reaper_3_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_3.reapIntegralFor(deployer) == (reaper_3.lastUnitCostIntegralFor(
        deployer) - last_reaper_3_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_3_reap_integral_deployer
    assert reaper_3.reapIntegralFor(morpheus) == (reaper_3.lastUnitCostIntegralFor(
        morpheus) - last_reaper_3_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_3_reap_integral_deployer
    assert reaper_3.reapIntegralFor(
        deployer) == reaper_3.reapIntegralFor(morpheus)
    assert reaper_3.lastSnapshotTimestamp() == tx16.timestamp
    assert reaper_3.lastSnapshotTimestampFor(deployer) == tx16.timestamp
    assert reaper_3.lastSnapshotTimestampFor(morpheus) == tx16.timestamp
    voting_koeff_3_full = reaper_3.voteIntegral(
    ) / (tx16.timestamp - tx_emission.timestamp) / VOTE_DIVIDER
    assert abs(reaper_3.voteIntegral() / (tx16.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.119) < 10 ** (-3)
    assert abs(reaper_3.voteIntegral() / (tx16.timestamp -
               reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER - 0.277) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_3) == 0
    assert reaper_3.boostIntegralFor(deployer) == 0
    assert reaper_3.totalBoostIntegralFor(deployer) == 0
    assert reaper_3.boostIntegralFor(morpheus) == 0
    assert reaper_3.totalBoostIntegralFor(morpheus) == 0
    last_reaper_3_balances_integral = reaper_3.balancesIntegral()
    last_reaper_3_emission_integral = reaper_3.emissionIntegral()
    last_reaper_3_vote_integral = reaper_3.voteIntegral()
    last_reaper_3_unit_cost_integral = reaper_3.unitCostIntegral()
    last_reaper_3_reap_integral_deployer = reaper_3.reapIntegralFor(deployer)
    last_reaper_3_reap_integral_morpheus = reaper_3.reapIntegralFor(morpheus)

    # check emission share
    distributed_emission = (reaper_3.emissionIntegral() -
                            previous_emission_integral) // 2
    assert distributed_emission_reaper_2 // distributed_emission_reaper_3 > 10 ** 4
    assert distributed_emission_reaper == distributed_emission_reaper_2
    previous_emission_integral = reaper_3.emissionIntegral()
    print("--------")
    print(distributed_emission, "distributed_emission")
    print(distributed_emission_reaper, "distributed_emission_reaper")
    print(distributed_emission_reaper_2, "distributed_emission_reaper_2")
    print(distributed_emission_reaper_3, "distributed_emission_reaper_3")
    print("--------")
    assert abs(distributed_emission - distributed_emission_reaper -
               distributed_emission_reaper_2 - distributed_emission_reaper_3) < 10 ** 8
    assert abs(voting_koeff + voting_koeff_2 +
               voting_koeff_3_full - 1) < 10 ** (-3)

    # wait till next voting period
    chain.mine(1, aligned_time + 7 * week)

    # snapshot reaper
    while True:
        chain.mine(1, aligned_time + 7 * week + week - 10)
        tx17 = reaper.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 7 * week + week - 10)
        tx17_1 = reaper.snapshot({'from': morpheus})
        if tx17.timestamp == tx17_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * \
        (tx17.timestamp - tx_emission.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * \
        (tx17.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_integral) * (reaper.voteIntegral() -
                                                                                                last_vote_integral) // (reaper.balancesIntegral() - last_balances_integral) + last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.unitCostIntegral()
    assert reaper.lastUnitCostIntegralFor(
        morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(
        deployer) + reaper.reapIntegralFor(morpheus)
    voting_koeff = reaper.voteIntegral() / (tx17.timestamp -
                                            tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 2 *
               voting_koeff) <= 10 ** 8  # reaper share=voting_koeff, no boosts
    distributed_emission_reaper = (reaper.unitCostIntegral(
    ) - last_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(
        deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(
        morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reap_integral_morpheus
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus)
    assert reaper.lastSnapshotTimestamp() == tx17.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx17.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx17.timestamp
    assert abs(reaper.voteIntegral() / (tx17.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.385) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper) == 500000000000000000
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_integral = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # snapshot reaper_2 (check that reaper_2 got correct value)
    while True:
        chain.mine(1, aligned_time + 7 * week + week - 10)
        tx18 = reaper_2.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 7 * week + week - 10)
        tx18_1 = reaper_2.snapshot({'from': morpheus})
        if tx18.timestamp == tx18_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_2.balances(deployer) == amount
    assert reaper_2.balances(morpheus) == amount
    assert reaper_2.totalBalances() == 2 * amount
    assert reaper_2.balancesIntegral() == 2 * amount * \
        (tx18.timestamp - tx_emission.timestamp)
    assert reaper_2.balancesIntegralFor(
        deployer) == reaper_2.balancesIntegral()
    assert reaper_2.balancesIntegralFor(
        morpheus) == reaper_2.balancesIntegral()
    assert reaper_2.emissionIntegral() == YEAR_EMISSION * \
        (tx18.timestamp - tx_emission.timestamp) // year
    assert reaper_2.unitCostIntegral() == (reaper_2.emissionIntegral() - last_reaper_2_emission_integral) * (reaper_2.voteIntegral() -
                                                                                                             last_reaper_2_vote_integral) // (reaper_2.balancesIntegral() - last_reaper_2_balances_integral) + last_reaper_2_unit_cost_integral
    assert reaper_2.lastUnitCostIntegralFor(
        deployer) == reaper_2.unitCostIntegral()
    assert reaper_2.lastUnitCostIntegralFor(
        morpheus) == reaper_2.unitCostIntegral()
    assert reaper_2.reapIntegral() == reaper_2.reapIntegralFor(
        deployer) + reaper_2.reapIntegralFor(morpheus)
    voting_koeff_2 = reaper_2.voteIntegral() / (tx18.timestamp -
                                                tx_emission.timestamp) / VOTE_DIVIDER
    print(voting_koeff_2)
    assert abs(reaper_2.reapIntegral() - reaper_2.emissionIntegral() // 2 *
               voting_koeff_2) <= 10 ** 8  # reaper_2 share=voting_koeff_2, no boosts
    distributed_emission_reaper_2 = (reaper_2.unitCostIntegral(
    ) - last_reaper_2_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_2.reapIntegralFor(deployer) == (reaper_2.lastUnitCostIntegralFor(
        deployer) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(morpheus) == (reaper_2.lastUnitCostIntegralFor(
        morpheus) - last_reaper_2_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_2_reap_integral_deployer
    assert reaper_2.reapIntegralFor(
        deployer) == reaper_2.reapIntegralFor(morpheus)
    assert reaper_2.lastSnapshotTimestamp() == tx18.timestamp
    assert reaper_2.lastSnapshotTimestampFor(deployer) == tx18.timestamp
    assert reaper_2.lastSnapshotTimestampFor(morpheus) == tx18.timestamp
    assert abs(reaper_2.voteIntegral() / (tx18.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.511) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_2) == 500000000000000000
    assert reaper_2.boostIntegralFor(deployer) == 0
    assert reaper_2.totalBoostIntegralFor(deployer) == 0
    assert reaper_2.boostIntegralFor(morpheus) == 0
    assert reaper_2.totalBoostIntegralFor(morpheus) == 0
    last_reaper_2_balances_integral = reaper_2.balancesIntegral()
    last_reaper_2_emission_integral = reaper_2.emissionIntegral()
    last_reaper_2_vote_integral = reaper_2.voteIntegral()
    last_reaper_2_unit_cost_integral = reaper_2.unitCostIntegral()
    last_reaper_2_reap_integral_deployer = reaper_2.reapIntegralFor(deployer)
    last_reaper_2_reap_integral_morpheus = reaper_2.reapIntegralFor(morpheus)

    # snapshot reaper_3 (check that reaper_3 got correct value)
    while True:
        chain.mine(1, aligned_time + 7 * week + week - 10)
        tx19 = reaper_3.snapshot({'from': deployer})
        chain.mine(1, aligned_time + 7 * week + week - 10)
        tx19_1 = reaper_3.snapshot({'from': morpheus})
        if tx19.timestamp == tx19_1.timestamp:
            break
        else:
            chain.undo(2)

    assert reaper_3.balances(deployer) == amount
    assert reaper_3.balances(morpheus) == amount
    assert reaper_3.totalBalances() == 2 * amount
    assert reaper_3.balancesIntegral() == 2 * amount * \
        (tx19.timestamp - tx7.timestamp)
    assert reaper_3.balancesIntegralFor(
        deployer) == reaper_3.balancesIntegral()
    assert reaper_3.balancesIntegralFor(
        morpheus) == reaper_3.balancesIntegral()
    assert reaper_3.emissionIntegral() == YEAR_EMISSION * \
        (tx19.timestamp - tx_emission.timestamp) // year
    assert reaper_3.unitCostIntegral() == (reaper_3.emissionIntegral() - last_reaper_3_emission_integral) * (reaper_3.voteIntegral() -
                                                                                                             last_reaper_3_vote_integral) // (reaper_3.balancesIntegral() - last_reaper_3_balances_integral) + last_reaper_3_unit_cost_integral
    assert reaper_3.lastUnitCostIntegralFor(
        deployer) == reaper_3.unitCostIntegral()
    assert reaper_3.lastUnitCostIntegralFor(
        morpheus) == reaper_3.unitCostIntegral()
    assert reaper_3.reapIntegral() == reaper_3.reapIntegralFor(
        deployer) + reaper_3.reapIntegralFor(morpheus)
    voting_koeff_3 = reaper_3.voteIntegral() / (tx19.timestamp -
                                                reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER
    print(voting_koeff_3)
    assert abs(reaper_3.reapIntegral() - (reaper_3.emissionIntegral() - init_reaper_3_emission_integral) //
               2 * voting_koeff_3) <= 10 ** 8  # reaper_3 share=voting_koeff_3, no boosts
    distributed_emission_reaper_3 = (reaper_3.unitCostIntegral(
    ) - last_reaper_3_unit_cost_integral) * amount * 2 // 2 // VOTE_DIVIDER
    assert reaper_3.reapIntegralFor(deployer) == (reaper_3.lastUnitCostIntegralFor(
        deployer) - last_reaper_3_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_3_reap_integral_deployer
    assert reaper_3.reapIntegralFor(morpheus) == (reaper_3.lastUnitCostIntegralFor(
        morpheus) - last_reaper_3_unit_cost_integral) * amount // 2 // VOTE_DIVIDER + last_reaper_3_reap_integral_deployer
    assert reaper_3.reapIntegralFor(
        deployer) == reaper_3.reapIntegralFor(morpheus)
    assert reaper_3.lastSnapshotTimestamp() == tx19.timestamp
    assert reaper_3.lastSnapshotTimestampFor(deployer) == tx19.timestamp
    assert reaper_3.lastSnapshotTimestampFor(morpheus) == tx19.timestamp
    voting_koeff_3_full = reaper_3.voteIntegral(
    ) / (tx19.timestamp - tx_emission.timestamp) / VOTE_DIVIDER
    assert abs(reaper_3.voteIntegral() / (tx19.timestamp -
               tx_emission.timestamp) / VOTE_DIVIDER - 0.104) < 10 ** (-3)
    assert abs(reaper_3.voteIntegral() / (tx19.timestamp -
               reaper_3_init_timestamp.timestamp) / VOTE_DIVIDER - 0.208) < 10 ** (-3)
    assert voting_controller.lastVotes(reaper_3) == 0
    assert reaper_3.boostIntegralFor(deployer) == 0
    assert reaper_3.totalBoostIntegralFor(deployer) == 0
    assert reaper_3.boostIntegralFor(morpheus) == 0
    assert reaper_3.totalBoostIntegralFor(morpheus) == 0
    last_reaper_3_balances_integral = reaper_3.balancesIntegral()
    last_reaper_3_emission_integral = reaper_3.emissionIntegral()
    last_reaper_3_vote_integral = reaper_3.voteIntegral()
    last_reaper_3_unit_cost_integral = reaper_3.unitCostIntegral()
    last_reaper_3_reap_integral_deployer = reaper_3.reapIntegralFor(deployer)
    last_reaper_3_reap_integral_morpheus = reaper_3.reapIntegralFor(morpheus)

    # check emission share
    distributed_emission = (reaper_3.emissionIntegral() -
                            previous_emission_integral) // 2
    assert distributed_emission_reaper_3 == 0
    assert distributed_emission_reaper == distributed_emission_reaper_2
    previous_emission_integral = reaper_3.emissionIntegral()
    print("--------")
    print(distributed_emission, "distributed_emission")
    print(distributed_emission_reaper, "distributed_emission_reaper")
    print(distributed_emission_reaper_2, "distributed_emission_reaper_2")
    print(distributed_emission_reaper_3, "distributed_emission_reaper_3")
    print("--------")
    assert abs(distributed_emission - distributed_emission_reaper -
               distributed_emission_reaper_2 - distributed_emission_reaper_3) < 10 ** 8
    assert abs(voting_koeff + voting_koeff_2 +
               voting_koeff_3_full - 1) < 10 ** (-3)
