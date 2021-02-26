from brownie.test import given, strategy


VOTE_DIVIDER = 10 ** 18
YEAR_EMISSION = 1_000_000 * 10 ** 18


@given(amount=strategy('uint256', min_value=1_000, max_value=1_000_000))
def test_deposit(farm_token, lp_token, reaper, voting_controller, deployer, thomas, MAX_UINT256, chain, day, amount):
    initial_balance = lp_token.balanceOf(deployer)
    lp_token.approve(reaper, MAX_UINT256, {'from': deployer})
    init_ts = chain.time()
    chain.mine(1, init_ts)
    farm_token.startEmission({'from': deployer})
    chain.mine(1, init_ts)
    voting_controller.snapshot({'from': deployer})
    assert reaper.balances(deployer) == 0
    assert reaper.totalBalances() == 0
    assert reaper.balancesIntegral() == 0
    assert reaper.balancesIntegralFor(deployer) == 0
    assert reaper.reapIntegral() == 0
    assert reaper.reapIntegralFor(deployer) == 0
    assert reaper.unitCostIntegral() == 0
    assert reaper.lastUnitCostIntegralFor(deployer) == 0
    assert reaper.lastSnapshotTimestamp() == 0
    assert reaper.lastSnapshotTimestampFor(deployer) == 0
    assert reaper.emissionIntegral() == 0
    assert reaper.voteIntegral() == 0
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0

    chain.mine(1, init_ts)
    tx2 = reaper.deposit(amount, {'from': deployer})
    assert lp_token.balanceOf(reaper) == amount
    assert lp_token.balanceOf(deployer) == initial_balance - amount
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == 0
    assert reaper.balancesIntegralFor(deployer) == 0
    assert reaper.reapIntegral() == 0
    assert reaper.reapIntegralFor(deployer) == 0
    assert reaper.unitCostIntegral() == 0
    assert reaper.lastUnitCostIntegralFor(deployer) == 0
    assert reaper.lastSnapshotTimestamp() == tx2.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx2.timestamp
    assert reaper.emissionIntegral() == 0
    assert reaper.voteIntegral() == (
        tx2.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0

    chain.mine(1, tx2.timestamp + day)
    tx3 = reaper.snapshot({'from': deployer})
    assert reaper.balances(deployer) == amount
    assert reaper.totalBalances() == amount
    assert reaper.balancesIntegral() == amount * (tx3.timestamp - tx2.timestamp)
    assert reaper.balancesIntegralFor(
        deployer) == amount * (tx3.timestamp - tx2.timestamp)

    assert abs(reaper.emissionIntegral() - YEAR_EMISSION / 365) < 10 ** 10
    assert reaper.reapIntegral() == reaper.reapIntegralFor(deployer)
    assert reaper.emissionIntegral() / 2 - reaper.reapIntegralFor(deployer) < 1
    assert reaper.unitCostIntegral() == reaper.lastUnitCostIntegralFor(deployer)
    assert reaper.lastSnapshotTimestamp() == tx3.timestamp
    assert reaper.lastSnapshotTimestampFor(deployer) == tx3.timestamp
    assert reaper.lastUnitCostIntegralFor(
        deployer) == reaper.emissionIntegral() * reaper.voteIntegral() / amount
    # assert reaper.voteIntegral() == (
    #     tx2.timestamp - voting_controller.lastSnapshotTimestamp()) * VOTE_DIVIDER
    assert reaper.boostIntegralFor(deployer) == 0
    assert reaper.totalBoostIntegralFor(deployer) == 0
    # lp_token.transfer(thomas, 2 * amount, {'from': deployer})
    # lp_token.approve(reaper, MAX_UINT256, {'from': thomas})
    # reaper.deposit(2 * amount, {'from': thomas})
    # assert lp_token.balanceOf(reaper) == 3 * amount
    # assert lp_token.balanceOf(thomas) == 0

    # chain.mine(1, chain.time() + day)
    # reaper.withdraw(2 * amount, {'from': deployer})
    # assert lp_token.balanceOf(reaper) == 0
    # assert lp_token.balanceOf(deployer) == initial_balance
