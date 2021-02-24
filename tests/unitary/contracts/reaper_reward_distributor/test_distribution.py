import brownie
from brownie.test import given, strategy

@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_distribution(reaper_reward_distributor_mocked, reaper_mock, ZERO_ADDRESS, lp_token, usdn_token, farm_token, neo, morpheus, trinity, amount, day, delta):
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, neo)
    assert tx.return_value == 0
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus)
    assert tx.return_value == 0
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity)
    assert tx.return_value == 0

    # make deposits on reaper_mock for morpheus
    lp_token.transfer(morpheus, 100, {'from': neo})
    lp_token.approve(reaper_mock, 100, {'from': morpheus})

    brownie.chain.mine(1, brownie.chain.time() + 1)
    reaper_mock.deposit(100, {'from': morpheus})
    block_timestamp_1 = brownie.chain.time()

    assert block_timestamp_1 - reaper_mock.lastReapTimestamp() <= 5
    assert block_timestamp_1 - reaper_mock.lastReapTimestampFor(morpheus) <= 5
    block_timestamp_1 = reaper_mock.lastReapTimestampFor(morpheus)

    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus)
    assert tx.return_value == 0
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity)
    assert tx.return_value == 0 

    # add some reward in usdn
    usdn_token.deposit(reaper_reward_distributor_mocked, 100, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 100

    brownie.chain.mine(1, block_timestamp_1 + day + delta)

    reaper_mock.snapshot(morpheus)
    block_timestamp_2 = brownie.chain.time()

    assert block_timestamp_2 - reaper_mock.lastReapTimestamp() <= 5
    assert block_timestamp_2 - reaper_mock.lastReapTimestampFor(morpheus) <= 5
    block_timestamp_2 = reaper_mock.lastReapTimestampFor(morpheus)

    assert reaper_mock.reapIntegralFor(morpheus) == 100 * (block_timestamp_2 - block_timestamp_1)
    assert reaper_mock.reapIntegral() == 100 * (block_timestamp_2 - block_timestamp_1)

    # claim all the reward
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus, {'from': morpheus})
    assert tx.return_value == 100

    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 0
    assert usdn_token.balanceOf(morpheus) == 100

    # make deposits on reaper_mock for trinity
    lp_token.transfer(trinity, 100, {'from': neo})
    lp_token.approve(reaper_mock, 100, {'from': trinity})
    reaper_mock.deposit(100, {'from': trinity})

    block_timestamp_3 = brownie.chain.time()

    assert block_timestamp_3 - reaper_mock.lastReapTimestamp() <= 5
    assert block_timestamp_3 - reaper_mock.lastReapTimestampFor(trinity) <= 5
    block_timestamp_3_morpheus = reaper_mock.lastReapTimestampFor(morpheus)
    block_timestamp_3_trinity = reaper_mock.lastReapTimestampFor(trinity)

    assert reaper_mock.reapIntegralFor(morpheus) == 100 * (block_timestamp_3_morpheus - block_timestamp_1)
    assert reaper_mock.reapIntegralFor(trinity) == 0
    assert reaper_mock.reapIntegral() == 100 * (block_timestamp_3_morpheus - block_timestamp_1)

    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus)
    assert tx.return_value == 0
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity)
    assert tx.return_value == 0

    # add some reward in usdn again
    usdn_token.deposit(reaper_reward_distributor_mocked, 400, {'from': neo})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 400

    brownie.chain.mine(1, brownie.chain.time() + day + delta)

    reaper_mock.snapshot(morpheus)
    reaper_mock.snapshot(trinity)
    block_timestamp_4 = brownie.chain.time()

    assert block_timestamp_4 - reaper_mock.lastReapTimestamp() <= 5
    assert block_timestamp_4 - reaper_mock.lastReapTimestampFor(morpheus) <= 5
    assert block_timestamp_4 - reaper_mock.lastReapTimestampFor(trinity) <= 5
    block_timestamp_4_morpheus = reaper_mock.lastReapTimestampFor(morpheus)
    block_timestamp_4_trinity = reaper_mock.lastReapTimestampFor(trinity)

    assert reaper_mock.reapIntegralFor(morpheus) == 100 * (block_timestamp_4_morpheus - block_timestamp_1)
    assert reaper_mock.reapIntegralFor(trinity) - (100 * (block_timestamp_4_trinity - block_timestamp_3_trinity)) <= 10
    assert reaper_mock.reapIntegral() - (100 * (block_timestamp_4_morpheus - block_timestamp_1) + 100 * (block_timestamp_4_trinity - block_timestamp_3_trinity)) <= 10

    print("____--____")
    print(reaper_mock.reapIntegralFor(morpheus))
    print(reaper_mock.reapIntegralFor(trinity))
    print(reaper_mock.reapIntegral())

    # check for the reward
    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, morpheus, {'from': morpheus})
    assert tx.return_value - 200 <= 1

    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity, {'from': trinity})
    assert tx.return_value - 166 <= 1

    # claim reward for morpheus
    tx = reaper_reward_distributor_mocked.claim(usdn_token, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert usdn_token.balanceOf(reaper_reward_distributor_mocked) == 200
    assert usdn_token.balanceOf(morpheus) == 300

    tx = reaper_reward_distributor_mocked.claimableTokens(usdn_token, trinity, {'from': trinity})
    assert tx.return_value - 233 <= 1 # TODO: INCONSISTENT

    # TODO: check event

    pass
