import brownie, math
from brownie.test import given, strategy

week = 604800

def test_boost_wrong_token(boosting_controller, usdn_token, neo, exception_tester):
    exception_tester("invalid coin", boosting_controller.boost, usdn_token, 1, 1, {'from': neo})


def test_boost_zero_amount(boosting_controller, farm_token, neo, exception_tester):
    exception_tester("zero amount", boosting_controller.boost, farm_token, 0, 1, {'from': neo})


def test_boost_short_locktime(boosting_controller, farm_token, neo, exception_tester):
    exception_tester("locktime is too short", boosting_controller.boost, farm_token, 1, 1, {'from': neo})


def test_boost_farm_token_not_approved(boosting_controller, farm_token, neo):
    with brownie.reverts():
        boosting_controller.boost(farm_token, 1, boosting_controller.minLockingPeriod(), {'from': neo})


# @given(amount=strategy('uint256', min_value=10**10, max_value=10**13))
def test_boost_farm_token(boosting_controller, farm_token, neo, morpheus):
    amount = 10**10
    delta = 86400
    minLockTime = boosting_controller.minLockingPeriod()

    # boost with farm_token 1st time
    farm_token.approve(boosting_controller, 5 * amount, {'from': neo})
    tx1 = boosting_controller.boost(farm_token, amount, minLockTime, {'from': neo})
    blockTimestamp = brownie.chain.time()

    # check tx1 event
    assert tx1.return_value is None
    assert len(tx1.events) == 2
    assert tx1.events["Boost"].values() == [farm_token, neo, amount]

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert boosting_controller.boostIntegral() == 0
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller.lastBoostTimestamp()
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(neo) == 0
    assert boosting_controller.lastBoostTimestampFor(neo) == blockTimestamp

    # wait for some time (quater of warmup - delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 4 - delta)

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert boosting_controller.boostIntegral() == 0
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() == 0    
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(neo) == 0
    assert boosting_controller.lastBoostTimestampFor(neo) == blockTimestamp

    # wait for some time (up to quater of warmup)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 4)

    tx2 = boosting_controller.commonBoostIntegral()
    tx3 = boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(neo)
    instant_value_1 = boosting_controller.boosts(neo)[1]
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[1] == amount * (blockTimestamp_1 - blockTimestamp) / boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(neo) == (instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2
    assert tx2.return_value == boosting_controller.boostIntegral()
    assert tx3.return_value == boosting_controller.boostIntegralFor(neo)

    # wait for some time (up to half of warmup + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 2 + delta)

    tx2 = boosting_controller.commonBoostIntegral()
    tx3 = boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(neo)
    instant_value_2 = boosting_controller.boosts(neo)[1]
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[1] == amount * (blockTimestamp_2 - blockTimestamp) / boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(neo) == math.floor((instant_value_2 + instant_value_1) * (blockTimestamp_2 - blockTimestamp_1) / 2) + math.floor((instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2)
    assert tx2.return_value == boosting_controller.boostIntegral()
    assert tx3.return_value == boosting_controller.boostIntegralFor(neo)
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)

    # wait for some time (end of warmup + quater of reduction)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime / 4)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_3 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_3 = boosting_controller.lastBoostTimestampFor(neo)
    instant_value_3 = boosting_controller.boosts(neo)[1]
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(neo)[1] == amount - math.floor((blockTimestamp_3 - boosting_controller.boosts(neo)[2]) * (amount - math.floor(amount / 2)) / (boosting_controller.boosts(neo)[3] - boosting_controller.boosts(neo)[2]))
    assert boosting_controller.boostIntegralFor(neo) == math.floor((instant_value_3 + amount) * (blockTimestamp_3 - boosting_controller.boosts(neo)[2]) / 2) + math.floor((amount + instant_value_2) * (boosting_controller.boosts(neo)[2] - blockTimestamp_2) / 2) + previous_integral_neo
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)

    # wait for some time (end of warmup + 3/4 of reduction)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime * 3 / 4)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_4 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_4 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_4 = boosting_controller.lastBoostTimestampFor(neo)
    instant_value_4 = boosting_controller.boosts(neo)[1]
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(neo)[1] == amount - math.floor((blockTimestamp_4 - boosting_controller.boosts(neo)[2]) * (amount - math.floor(amount / 2)) / (boosting_controller.boosts(neo)[3] - boosting_controller.boosts(neo)[2]))
    assert boosting_controller.boostIntegralFor(neo) == math.floor((instant_value_4 + instant_value_3) * (blockTimestamp_4 - blockTimestamp_3) / 2) + previous_integral_neo
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)

    # wait for some time (end of reduction + week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime + week)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_5 = brownie.chain.time()
    
    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_5 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_5 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_5 = boosting_controller.lastBoostTimestampFor(neo)
    instant_value_5 = boosting_controller.boosts(neo)[1]
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(neo)[1] == amount - math.floor(amount / 2)
    assert boosting_controller.boostIntegralFor(neo) == math.floor((instant_value_5 + instant_value_5) * (blockTimestamp_5 - boosting_controller.boosts(neo)[3]) / 2) + math.floor((instant_value_5 + instant_value_4) * (boosting_controller.boosts(neo)[3] - blockTimestamp_4) / 2) + previous_integral_neo
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)

    # wait for some time (end of reduction + 2 * week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime + 2 * week)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_6 = brownie.chain.time()
    
    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_6 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_6 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_6 = boosting_controller.lastBoostTimestampFor(neo)
    instant_value_6 = boosting_controller.boosts(neo)[1]
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(neo)[1] == amount - math.floor(amount / 2)
    assert boosting_controller.boostIntegralFor(neo) == math.floor((instant_value_6 + instant_value_6) * (blockTimestamp_6 - blockTimestamp_5) / 2) + previous_integral_neo







    # with brownie.reverts():
    #     voting_controller.vote(
    #         three_reapers_stub[0], farm_token, amount, {'from': neo})

    # initial_balance = farm_token.balanceOf(neo)
    # farm_token.approve(voting_controller, amount, {'from': neo})
    # tx1 = voting_controller.vote(
    #     three_reapers_stub[0], farm_token, amount, {'from': neo})

    # assert tx1.return_value is None
    # assert len(tx1.events) == 2
    # assert tx1.events["Transfer"].values() == [neo, voting_controller, amount]
    # assert tx1.events["Vote"].values(
    # ) == [three_reapers_stub[0], farm_token, neo, amount]

    # with brownie.reverts():
    #     voting_controller.vote(
    #         three_reapers_stub[0], farm_token, amount, {'from': neo})

    # assert farm_token.balanceOf(neo) == initial_balance - amount
    # assert farm_token.balanceOf(voting_controller) == amount
    # assert voting_controller.reaperBalances(
    #     three_reapers_stub[0], farm_token) == amount
    # assert voting_controller.balances(
    #     three_reapers_stub[0], farm_token, neo) == amount
    # assert voting_controller.accountVotePower(
    #     three_reapers_stub[0], neo) == amount
    # assert voting_controller.availableToUnvote(
    #     three_reapers_stub[0], farm_token, neo) == 0

    # with brownie.reverts("tokens are locked"):
    #     voting_controller.unvote(
    #         three_reapers_stub[0], farm_token, amount, {'from': neo})

    # brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

    # assert voting_controller.availableToUnvote(
    #     three_reapers_stub[0], farm_token, neo) == amount

    # tx2 = voting_controller.unvote(
    #     three_reapers_stub[0], farm_token, amount, {'from': neo})

    # assert tx2.return_value is None
    # assert len(tx2.events) == 2
    # assert tx2.events["Transfer"].values() == [voting_controller, neo, amount]
    # assert tx2.events["Unvote"].values(
    # ) == [three_reapers_stub[0], farm_token, neo, amount]

    # assert farm_token.balanceOf(neo) == initial_balance
    # assert farm_token.balanceOf(voting_controller) == 0
    # assert voting_controller.reaperBalances(
    #     three_reapers_stub[0], farm_token) == 0
    # assert voting_controller.balances(
    #     three_reapers_stub[0], farm_token, neo) == 0
    # assert voting_controller.accountVotePower(
    #     three_reapers_stub[0], neo) == 0
    # assert voting_controller.availableToUnvote(
    #     three_reapers_stub[0], farm_token, neo) == 0


# @given(amount=strategy('uint256', min_value=1, max_value=10**3))
# def test_vote_delegated(voting_controller, farm_token, three_reapers_stub, neo, morpheus, trinity, amount):
#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': morpheus})

#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': neo})

#     with brownie.reverts("voting approve required"):
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     with brownie.reverts("voting approve required"):
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, morpheus, {'from': neo})

#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, morpheus, neo)

#     tx1 = voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, True, {'from': neo})
#     assert voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, morpheus, neo)

#     initial_balance = farm_token.balanceOf(neo)
#     farm_token.approve(voting_controller, 2*amount, {'from': neo})

#     voting_controller.vote(
#         three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     assert farm_token.balanceOf(neo) == initial_balance - amount
#     assert farm_token.balanceOf(voting_controller) == amount
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == amount
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == amount
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0 # amount
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == amount

#     tx2 = voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, False, {'from': neo})
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)

#     with brownie.reverts("voting approve required"):
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     with brownie.reverts("voting approve required"):
#         voting_controller.unvote(
#             three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, True, {'from': neo})
#     assert voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)

#     voting_controller.vote(
#         three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     assert farm_token.balanceOf(neo) == initial_balance - 2*amount
#     assert farm_token.balanceOf(voting_controller) == 2*amount
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == 2*amount
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == 2*amount
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == 2*amount

#     with brownie.reverts("tokens are locked"):
#         voting_controller.unvote(
#             three_reapers_stub[0], farm_token, 2*amount, neo, {'from': morpheus})

#     brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

#     voting_controller.unvote(
#         three_reapers_stub[0], farm_token, 2*amount, neo, {'from': morpheus})

#     assert farm_token.balanceOf(neo) == initial_balance
#     assert farm_token.balanceOf(voting_controller) == 0
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == 0
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == 0

#     voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, False, {'from': neo})
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)

#     assert tx1.return_value is None
#     assert len(tx1.events) == 1
#     assert tx1.events["VoteApproval"].values(
#     ) == [three_reapers_stub[0], farm_token, neo, morpheus, True]

#     assert tx2.return_value is None
#     assert len(tx2.events) == 1
#     assert tx2.events["VoteApproval"].values(
#     ) == [three_reapers_stub[0], farm_token, neo, morpheus, False]
