VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18


def test_complex_voting(farm_token, lp_token, reaper, reaper_2, controller, voting_controller, deployer, morpheus, trinity, thomas, MAX_UINT256, chain, year, day):
    amount = 10**20
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
    init_ts = chain.time()

    # deposit on reapers
    chain.mine(1, init_ts + day)
    tx1 = reaper.deposit(amount, {'from': deployer})
    chain.mine(1, init_ts + day)
    reaper_2.deposit(amount, {'from': deployer})

    chain.mine(1, init_ts + 2 * day)
    tx2 = reaper.deposit(amount, {'from': morpheus})
    chain.mine(1, init_ts + 2 * day)
    reaper_2.deposit(amount, {'from': morpheus})

    # try to make a snapshot now (zero integrals)
    chain.mine(1, init_ts + 3 * day)
    tx3 = reaper.snapshot({'from': deployer})
    chain.mine(1, init_ts + 3 * day)
    tx3 = reaper.snapshot({'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx3.timestamp - tx2.timestamp) + amount * (tx2.timestamp - tx1.timestamp)
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
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral = reaper.unitCostIntegral()

    # wait for 7 days
    # startVoting + startEmission
    chain.mine(1, init_ts + 7 * day)
    tx_voting = voting_controller.startVoting({'from': deployer})
    chain.mine(1, init_ts + 7 * day)
    tx_emission = farm_token.startEmission({'from': deployer})
    assert tx_voting.timestamp == tx_emission.timestamp

    # # init reaper and reaper_2 by making a snapshot (update)
    # chain.mine(1, init_ts + 7 * day)
    # reaper.snapshot({'from': deployer})
    # reaper.snapshot({'from': morpheus})

    # 1st snapshot for both on reaper after 1 day
    chain.mine(1, init_ts + 8 * day)
    tx4_1 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx4_1.timestamp - tx_emission.timestamp) #+ last_balances_integral
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx4_1.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - 0)
    assert reaper.lastUnitCostIntegralFor(deployer) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 4 // 2) <= 10 ** 8 # reaper share=50%, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER
    assert reaper.lastSnapshotTimestamp() == tx4_1.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx4_1.timestamp
    assert reaper.voteIntegral() == (tx4_1.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER // 2 # reaper share=50%
    assert reaper.voteIntegral() / (tx4_1.timestamp - voting_controller.lastSnapshotTimestamp()) / VOTE_DIVIDER == 0.5
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0

    chain.mine(1, init_ts + 8 * day)
    tx4_2 = reaper.snapshot({'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == 2 * amount
    assert reaper.balancesIntegral() == 2 * amount * (tx4_2.timestamp - tx_emission.timestamp) #+ last_balances_integral
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == YEAR_EMISSION * (tx4_2.timestamp - tx_emission.timestamp) // year
    assert reaper.unitCostIntegral() == (reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (reaper.balancesIntegral() - 0)
    assert reaper.lastUnitCostIntegralFor(morpheus) == reaper.unitCostIntegral()
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    assert abs(reaper.reapIntegral() - reaper.emissionIntegral() // 4) <= 10 ** 8 # reaper share=50%, no boosts
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(morpheus) == (reaper.lastUnitCostIntegralFor(morpheus) - last_unit_cost_integral) * amount // 2 // VOTE_DIVIDER
    assert reaper.reapIntegralFor(deployer) == reaper.reapIntegralFor(morpheus) # equal shares in reaper
    assert reaper.lastSnapshotTimestamp() == tx4_2.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx4_1.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx4_2.timestamp
    assert reaper.voteIntegral() == (tx4_2.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER // 2 # reaper share=50%
    assert reaper.voteIntegral() / (tx4_2.timestamp - voting_controller.lastSnapshotTimestamp()) / VOTE_DIVIDER == 0.5
    assert reaper.boostIntegralFor(morpheus) == 0
    assert reaper.totalBoostIntegralFor(morpheus) == 0
    last_balances_integral = reaper.balancesIntegral()
    last_emission_intergal = reaper.emissionIntegral()
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
    # wait till next voting period
    # snapshot reaper (see reduction)

    # modify vote share
    # wait till next voting period + some time

    # add new reaper
    # modify vote share
    # wait till next voting period

    # snapshot reaper
    # snapshot reaper_2 (check that reaper_2 got correct value)
    # snapshot reaper_3 (check that reaper_3 got correct value)

    # wait time in current voting period
    # snapshot reaper (check)

    # modify vote share 
    # wait till next voting period 

    # snapshot reaper
    # snapshot reaper_2
    # snapshot reaper_3

    # modify vote share (set zero share)

    # snapshot reaper
    # snapshot reaper_2
    # snapshot reaper_3

    # assert False
