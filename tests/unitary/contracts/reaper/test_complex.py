import math
from brownie.test import given, strategy


VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18


# @given(amount=strategy('uint256', min_value=1_000, max_value=1_000_000))
def test_deposit(farm_token, lp_token, reaper, voting_controller, deployer, morpheus, thomas, MAX_UINT256, chain, year, day):
    amount = 1000
    lp_token.transfer(morpheus, amount)
    initial_balance = lp_token.balanceOf(deployer)
    lp_token.approve(reaper, MAX_UINT256, {'from': deployer})
    lp_token.approve(reaper, MAX_UINT256, {'from': morpheus})
    init_ts = chain.time()
    chain.mine(1, init_ts)
    tx = farm_token.startEmission({'from': deployer})
    initial_emission_timestamp = tx.timestamp
    chain.mine(1, init_ts)
    tx = voting_controller.snapshot({'from': deployer})
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

    # 1st snapshot
    chain.mine(1, tx2.timestamp + day)
    tx3 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx3.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx3.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == int(YEAR_EMISSION * (tx3.timestamp - initial_emission_timestamp) // year)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.lastUnitCostIntegralFor(deployer) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // amount)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 1
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // VOTE_DIVIDER // (tx3.timestamp - tx2.timestamp) // 2
    assert reaper.lastSnapshotTimestamp() == tx3.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx3.timestamp
    assert reaper.voteIntegral() == (tx3.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # 2nd snapshot
    chain.mine(1, tx3.timestamp + day)
    tx4 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx4.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx4.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == int(YEAR_EMISSION * (tx4.timestamp - initial_emission_timestamp) // year)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.lastUnitCostIntegralFor(deployer) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // amount + last_unit_cost_integral)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 1
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // VOTE_DIVIDER // (tx4.timestamp - tx3.timestamp) // 2 + last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx4.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx4.timestamp
    assert reaper.voteIntegral() == (tx4.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # 3rd snapshot
    chain.mine(1, tx4.timestamp + day)
    tx5 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx5.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx5.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == int(YEAR_EMISSION * (tx5.timestamp - initial_emission_timestamp) // year)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.lastUnitCostIntegralFor(deployer) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // amount + last_unit_cost_integral)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 1
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // VOTE_DIVIDER // (tx5.timestamp - tx4.timestamp) // 2 + last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx5.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx5.timestamp
    assert reaper.voteIntegral() == (tx5.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # 4th snapshot
    chain.mine(1, tx5.timestamp + day)
    tx6 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.emissionIntegral() == int(YEAR_EMISSION * (tx6.timestamp - initial_emission_timestamp) // year)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.lastUnitCostIntegralFor(deployer) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // amount + last_unit_cost_integral)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert abs(reaper.reapIntegralFor(deployer) - reaper.emissionIntegral() // 2) <= 1
    assert reaper.reapIntegralFor(deployer) == (reaper.lastUnitCostIntegralFor(deployer) - last_unit_cost_integral) * amount // VOTE_DIVIDER // (tx6.timestamp - tx5.timestamp) // 2 + last_reap_integral_deployer
    assert reaper.lastSnapshotTimestamp() == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.voteIntegral() == (tx6.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral_deployer = reaper.lastUnitCostIntegralFor(deployer)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)

    # deposit amount for morpheus (snapshot for deployer has not been done for a day)
    # chain.mine(1, tx6.timestamp + day)
    # tx7 = reaper.snapshot({'from': deployer})
    chain.mine(1, tx6.timestamp + day)
    tx7 = reaper.deposit(amount, {'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    # assert reaper.balancesIntegral() == amount * (tx6.timestamp - tx2.timestamp) # not updated (gas optimization)
    # assert reaper.balancesIntegralFor(deployer) == amount * (tx6.timestamp - tx2.timestamp) # not updated for deployer
    assert reaper.balancesIntegralFor(morpheus) == 0
    assert reaper.emissionIntegral() == int(YEAR_EMISSION * (tx7.timestamp - initial_emission_timestamp) // year)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(morpheus)
    # assert reaper.lastUnitCostIntegralFor(deployer) == last_unit_cost_integral
    assert reaper.lastUnitCostIntegralFor(morpheus) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // amount + last_unit_cost_integral)
    # assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) # not updated (gas optimization)
    # assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == 0
    # assert reaper.lastSnapshotTimestamp() == tx6.timestamp # not updated (gas optimization)
    # assert reaper.lastSnapshotTimestampFor(deployer) == tx6.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx7.timestamp
    # assert reaper.reapIntegral() == last_reap_integral_deployer # not updated (gas optimization)
    assert reaper.voteIntegral() == (tx7.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_unit_cost_integral_morpheus = reaper.lastUnitCostIntegralFor(morpheus)
    last_reap_integral_deployer = reaper.reapIntegralFor(deployer)
    last_reap_integral_morpheus = reaper.reapIntegralFor(morpheus)

    # 5th snapshot for both
    chain.mine(1, tx7.timestamp + day)
    tx8 = reaper.snapshot({'from': deployer})
    chain.mine(1, tx7.timestamp + day)
    tx8 = reaper.snapshot({'from': morpheus})
    assert reaper.balances(deployer) == amount
    assert reaper.balances(morpheus) == amount
    assert reaper.totalBalances() == 2 * amount
    # assert reaper.balancesIntegral() == 2 * amount * (tx8.timestamp - tx6.timestamp) + amount * (tx6.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(deployer) == reaper.balancesIntegral()
    assert reaper.balancesIntegralFor(morpheus) == reaper.balancesIntegral()
    assert reaper.emissionIntegral() == int(YEAR_EMISSION * (tx8.timestamp - initial_emission_timestamp) // year)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(morpheus)
    assert reaper.lastUnitCostIntegralFor(deployer) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (2 * amount) + last_unit_cost_integral)
    assert reaper.lastUnitCostIntegralFor(morpheus) == int((reaper.emissionIntegral() - last_emission_intergal) * (reaper.voteIntegral() - last_vote_integral) // (2 * amount) + last_unit_cost_integral)
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer) + reaper.reapIntegralFor(morpheus)
    # assert reaper.reapIntegralFor(deployer) == (reaper.unitCostIntegral() - last_unit_cost_integral_deployer) * amount // VOTE_DIVIDER // (tx8.timestamp - tx6.timestamp) // 2 + last_reap_integral_deployer
    assert reaper.reapIntegralFor(morpheus) == (reaper.unitCostIntegral() - last_unit_cost_integral_morpheus) * amount // VOTE_DIVIDER // (tx8.timestamp - tx7.timestamp) // 2 + last_reap_integral_morpheus
    
    print("reapIntegral", reaper.reapIntegral())
    print("reaper.reapIntegralFor(deployer)", reaper.reapIntegralFor(deployer))
    print("reaper.reapIntegralFor(morpheus)", reaper.reapIntegralFor(morpheus))
    print("emissionIntegral", reaper.emissionIntegral())

    assert reaper.reapIntegral() == reaper.emissionIntegral() // 2
    assert reaper.reapIntegralFor(deployer) == last_reap_integral_deployer + (reaper.emissionIntegral() - last_emission_intergal) // 4
    assert reaper.reapIntegralFor(morpheus) == last_reap_integral_morpheus + (reaper.emissionIntegral() - last_emission_intergal) // 4

    assert reaper.lastSnapshotTimestamp() == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx8.timestamp
    assert reaper.lastSnapshotTimestampFor(morpheus) == tx8.timestamp
    assert reaper.voteIntegral() == (tx8.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    last_unit_cost_integral = reaper.unitCostIntegral()
    last_emission_intergal = reaper.emissionIntegral()
    last_vote_integral = reaper.voteIntegral()
    last_reap_integral = reaper.reapIntegral()
