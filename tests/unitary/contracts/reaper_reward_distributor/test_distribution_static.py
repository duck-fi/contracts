import brownie
from brownie.test import given, strategy

@given(amount=strategy('uint256', min_value=10**10, max_value=10**13))
def test_distribution_static(reaper_reward_distributor_mocked, reaper_mock, ZERO_ADDRESS, lp_token, waves_token, usdn_token, farm_token, neo, morpheus, trinity, thomas, amount, week):
    # make some deposits on reaper_mock
    lp_token.approve(reaper_mock, 5 * amount, {'from': neo})

    lp_token.transfer(morpheus, 5 * amount, {'from': neo})
    lp_token.approve(reaper_mock, 5 * amount, {'from': morpheus})

    lp_token.transfer(trinity, 5 * amount, {'from': neo})
    lp_token.approve(reaper_mock, 5 * amount, {'from': trinity})

    lp_token.transfer(thomas, 5 * amount, {'from': neo})
    lp_token.approve(reaper_mock, 5 * amount, {'from': thomas})

    # make deposits on reaper_mock for morpheus
    init_ts = brownie.chain.time()
    brownie.chain.mine(1, init_ts)
    tx1 = reaper_mock.deposit(2 * amount, {'from': neo})
    brownie.chain.mine(1, init_ts)
    tx2 = reaper_mock.deposit(1 * amount, {'from': morpheus})
    brownie.chain.mine(1, init_ts)
    tx3 = reaper_mock.deposit(1 * amount, {'from': trinity})

    initial_deposit_ts_neo = tx1.timestamp
    initial_deposit_ts_morpheus = tx2.timestamp
    initial_deposit_ts_trinity = tx3.timestamp

    assert initial_deposit_ts_neo == reaper_mock.lastReapTimestampFor(neo)
    assert initial_deposit_ts_morpheus == reaper_mock.lastReapTimestampFor(morpheus)
    assert initial_deposit_ts_trinity == reaper_mock.lastReapTimestampFor(trinity)
    assert initial_deposit_ts_trinity == reaper_mock.lastReapTimestamp()
    initial_reap_integral = reaper_mock.reapIntegral()
    initial_reap_integral_ts = initial_deposit_ts_trinity

    # add some reward in usdn
    usdn_token.deposit(reaper_reward_distributor_mocked, 8 * amount, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 8 * amount

    # add some reward in waves
    waves_token.deposit(reaper_reward_distributor_mocked, 100 * amount, {'from': neo})
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 100 * amount

    # wait for 1 week
    brownie.chain.mine(1, brownie.chain.time() + week)

    # snapshot morpheus
    tx = reaper_mock.snapshot(morpheus)
    snapshot_ts_morpheus = tx.timestamp

    assert snapshot_ts_morpheus == reaper_mock.lastReapTimestampFor(morpheus)
    assert snapshot_ts_morpheus == reaper_mock.lastReapTimestamp()

    assert reaper_mock.reapIntegralFor(morpheus) == 1 * amount * (snapshot_ts_morpheus - initial_deposit_ts_morpheus)
    assert reaper_mock.reapIntegral() == 4 * amount * (snapshot_ts_morpheus - initial_reap_integral_ts) + initial_reap_integral
    assert abs(reaper_mock.reapIntegralFor(morpheus) / reaper_mock.reapIntegral() - 1/4) <= 0.00001

    # check claimable for morpheus
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 2 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 25 * amount

    # claim usdn reward for morpheus
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == 2 * amount
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 6 * amount

    assert len(tx.events) == 2
    assert tx.events["Claim"].values() == [usdn_token, morpheus, 2 * amount]

    # claim waves reward for morpheus
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == 25 * amount
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 75 * amount

    assert len(tx.events) == 2
    assert tx.events["Claim"].values() == [waves_token, morpheus, 25 * amount]

    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 0

    # snapshot neo
    tx = reaper_mock.snapshot(neo)
    snapshot_ts_neo = tx.timestamp

    assert snapshot_ts_neo == reaper_mock.lastReapTimestampFor(neo)
    assert snapshot_ts_neo == reaper_mock.lastReapTimestamp()

    assert reaper_mock.reapIntegralFor(neo) == 2 * amount * (snapshot_ts_neo - initial_deposit_ts_neo)
    assert reaper_mock.reapIntegral() == 4 * amount * (snapshot_ts_neo - initial_reap_integral_ts) + initial_reap_integral
    assert abs(reaper_mock.reapIntegralFor(neo) / reaper_mock.reapIntegral() - 1/2) <= 0.00001

    # check claimable for neo
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 4 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 50 * amount

    # snapshot trinity
    tx = reaper_mock.snapshot(trinity)
    snapshot_ts_trinity = tx.timestamp

    assert snapshot_ts_trinity == reaper_mock.lastReapTimestampFor(trinity)
    assert snapshot_ts_trinity == reaper_mock.lastReapTimestamp()

    assert reaper_mock.reapIntegralFor(trinity) == 1 * amount * (snapshot_ts_trinity - initial_deposit_ts_trinity)
    assert reaper_mock.reapIntegral() == 4 * amount * (snapshot_ts_trinity - initial_reap_integral_ts) + initial_reap_integral
    assert abs(reaper_mock.reapIntegralFor(trinity) / reaper_mock.reapIntegral() - 1/4) <= 0.00001

    # check claimable for trinity
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity) == 2 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, trinity) == 25 * amount

    # snapshot morpheus
    tx = reaper_mock.snapshot(morpheus)
    snapshot_ts_morpheus = tx.timestamp

    assert snapshot_ts_morpheus == reaper_mock.lastReapTimestampFor(morpheus)
    assert snapshot_ts_morpheus == reaper_mock.lastReapTimestamp()

    assert reaper_mock.reapIntegralFor(morpheus) == 1 * amount * (snapshot_ts_morpheus - initial_deposit_ts_morpheus)
    assert reaper_mock.reapIntegral() == 4 * amount * (snapshot_ts_morpheus - initial_reap_integral_ts) + initial_reap_integral
    assert abs(reaper_mock.reapIntegralFor(morpheus) / reaper_mock.reapIntegral() - 1/4) <= 0.00001

    # add some reward in usdn (8-neo, 4-trinity, 2-morpheus)
    usdn_token.deposit(reaper_reward_distributor_mocked, 8 * amount, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 14 * amount

    # add some reward in waves (100-neo, 75-trinity, 25-morpheus)
    waves_token.deposit(reaper_reward_distributor_mocked, 100 * amount, {'from': neo})
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 175 * amount

    # wait for 1 week
    brownie.chain.mine(1, brownie.chain.time() + week)

    # check claimable for morpheus
    reaper_mock.snapshot(morpheus)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 2 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 25 * amount

    # claim usdn reward for morpheus
    last_usdn_balance = usdn_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == 2 * amount + last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 12 * amount
    
    # try to claim usdn reward for morpheus again
    last_usdn_balance = usdn_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 12 * amount

    # claim waves reward for morpheus
    last_waves_balance = waves_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == 25 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 150 * amount

    # try to claim waves reward for morpheus again
    last_waves_balance = waves_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 150 * amount

    # check claimable for morpheus
    reaper_mock.snapshot(morpheus)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 0

    # check claimable for neo
    reaper_mock.snapshot(neo)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 8 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 100 * amount

    # claim usdn reward for neo
    last_usdn_balance = usdn_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, neo, ZERO_ADDRESS, {'from': neo})
    assert usdn_token.balanceOf(neo) == 8 * amount + last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 4 * amount

    # claim waves reward for neo
    last_waves_balance = waves_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(waves_token, neo, ZERO_ADDRESS, {'from': neo})
    assert waves_token.balanceOf(neo) == 100 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 50 * amount

    # check claimable for neo
    reaper_mock.snapshot(neo)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 0

    # add some reward in usdn (4-neo, 6-trinity, 2-morpheus)
    usdn_token.deposit(reaper_reward_distributor_mocked, 8 * amount, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 12 * amount

    # add some reward in waves (50-neo, 75-trinity, 25-morpheus)
    waves_token.deposit(reaper_reward_distributor_mocked, 100 * amount, {'from': neo})
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 150 * amount

    # wait for 1 week
    brownie.chain.mine(1, brownie.chain.time() + week)

    # check claimable for neo
    reaper_mock.snapshot(neo)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 4 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 50 * amount

    # claim usdn reward for neo
    last_neo_usdn_token_balance = usdn_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, neo, ZERO_ADDRESS, {'from': neo})
    assert usdn_token.balanceOf(neo) == 4 * amount + last_neo_usdn_token_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 8 * amount

    # claim waves reward for neo
    last_waves_balance = waves_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(waves_token, neo, ZERO_ADDRESS, {'from': neo})
    assert waves_token.balanceOf(neo) == 50 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 100 * amount

    # add some reward in usdn (2-neo, 7-trinity, 3-morpheus)
    usdn_token.deposit(reaper_reward_distributor_mocked, 4 * amount, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 12 * amount

    # add some reward in waves (200-neo, 175-trinity, 125-morpheus)
    waves_token.deposit(reaper_reward_distributor_mocked, 400 * amount, {'from': neo})
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 500 * amount

    # wait for 1 week
    brownie.chain.mine(1, brownie.chain.time() + week)

    # check claimable for neo
    reaper_mock.snapshot(neo)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 2 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 200 * amount

    # check claimable for morpheus
    reaper_mock.snapshot(morpheus)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 3 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 125 * amount

    # check claimable for trinity
    reaper_mock.snapshot(trinity)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity) == 7 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, trinity) == 175 * amount

    # claim usdn reward for morpheus
    last_usdn_balance = usdn_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == 3 * amount + last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 9 * amount

    # claim waves reward for morpheus
    last_waves_balance = waves_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == 125 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 375 * amount

    # try to claim usdn reward for morpheus again
    last_usdn_balance = usdn_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 9 * amount

    # try to claim waves reward for morpheus again
    last_waves_balance = waves_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 375 * amount

    # add some reward in usdn (4-neo, 8-trinity, 1-morpheus)
    usdn_token.deposit(reaper_reward_distributor_mocked, 4 * amount, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 13 * amount

    # add some reward in waves (300-neo, 225-trinity, 50-morpheus)
    waves_token.deposit(reaper_reward_distributor_mocked, 200 * amount, {'from': neo})
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 575 * amount

    # wait for 1 week
    brownie.chain.mine(1, brownie.chain.time() + week)

    # check claimable for neo
    reaper_mock.snapshot(neo)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 4 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 300 * amount

    # check claimable for morpheus
    reaper_mock.snapshot(morpheus)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 1 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 50 * amount

    # check claimable for trinity
    reaper_mock.snapshot(trinity)
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity) == 8 * amount
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, trinity) == 225 * amount

    # claim usdn reward for morpheus
    last_usdn_balance = usdn_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == 1 * amount + last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 12 * amount

    # claim waves reward for morpheus
    last_waves_balance = waves_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == 50 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 525 * amount

    # claim usdn reward for neo
    last_neo_usdn_token_balance = usdn_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, neo, ZERO_ADDRESS, {'from': neo})
    assert usdn_token.balanceOf(neo) == 4 * amount + last_neo_usdn_token_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 8 * amount

    # claim waves reward for neo
    last_waves_balance = waves_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(waves_token, neo, ZERO_ADDRESS, {'from': neo})
    assert waves_token.balanceOf(neo) == 300 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 225 * amount

    # claim usdn reward for trinity
    last_trinity_usdn_token_balance = usdn_token.balanceOf(trinity)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, trinity, ZERO_ADDRESS, {'from': trinity})
    assert usdn_token.balanceOf(trinity) == 8 * amount + last_trinity_usdn_token_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 0

    # claim waves reward for trinity
    last_waves_balance = waves_token.balanceOf(trinity)
    tx = reaper_reward_distributor_mocked.claim(waves_token, trinity, ZERO_ADDRESS, {'from': trinity})
    assert waves_token.balanceOf(trinity) == 225 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 0

    # check claimable for neo
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 0

    # check claimable for morpheus
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 0

    # check claimable for trinity
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, trinity) == 0

    # add some reward in usdn (2-neo, 1-trinity, 1-morpheus)
    usdn_token.deposit(reaper_reward_distributor_mocked, 4 * amount, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 4 * amount

    # add some reward in waves (50-neo, 25-trinity, 25-morpheus)
    waves_token.deposit(reaper_reward_distributor_mocked, 100 * amount, {'from': neo})
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 100 * amount

    # wait for 1 week
    brownie.chain.mine(1, brownie.chain.time() + week)

    # claim usdn reward for morpheus
    last_usdn_balance = usdn_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(morpheus) == 1 * amount + last_usdn_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 3 * amount

    # claim waves reward for morpheus
    last_waves_balance = waves_token.balanceOf(morpheus)
    tx = reaper_reward_distributor_mocked.claim(waves_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert waves_token.balanceOf(morpheus) == 25 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 75 * amount

    # claim usdn reward for neo
    last_neo_usdn_token_balance = usdn_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, neo, ZERO_ADDRESS, {'from': neo})
    assert usdn_token.balanceOf(neo) == 2 * amount + last_neo_usdn_token_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 1 * amount

    # claim waves reward for neo
    last_waves_balance = waves_token.balanceOf(neo)
    tx = reaper_reward_distributor_mocked.claim(waves_token, neo, ZERO_ADDRESS, {'from': neo})
    assert waves_token.balanceOf(neo) == 50 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 25 * amount

    # claim usdn reward for trinity
    last_trinity_usdn_token_balance = usdn_token.balanceOf(trinity)
    tx = reaper_reward_distributor_mocked.claim(usdn_token, trinity, ZERO_ADDRESS, {'from': trinity})
    assert usdn_token.balanceOf(trinity) == 1 * amount + last_trinity_usdn_token_balance
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 0

    # claim waves reward for trinity
    last_waves_balance = waves_token.balanceOf(trinity)
    tx = reaper_reward_distributor_mocked.claim(waves_token, trinity, ZERO_ADDRESS, {'from': trinity})
    assert waves_token.balanceOf(trinity) == 25 * amount + last_waves_balance
    assert waves_token.balanceOf(reaper_reward_distributor_mocked) == 0

    # check claimable for neo
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, neo) == 0

    # check claimable for morpheus
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, morpheus) == 0

    # check claimable for trinity
    assert reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity) == 0
    assert reaper_reward_distributor_mocked.claimableTokens(waves_token, trinity) == 0
