import brownie, math
from brownie.test import given, strategy

week = 604800

def test_boost_wrong_token(boosting_controller, usdn_token, neo, exception_tester):
    exception_tester("invalid coin", boosting_controller.boost, usdn_token, 1, 1, {'from': neo})


def test_boost_zero_amount(boosting_controller, farm_token, neo, exception_tester):
    exception_tester("zero amount", boosting_controller.boost, farm_token, 0, 1, {'from': neo})


def test_boost_short_locktime(boosting_controller, farm_token, neo, exception_tester):
    exception_tester("locktime is too short", boosting_controller.boost, farm_token, 1, 1, {'from': neo})


def test_boost_farm_token_not_approved(boosting_controller, farm_token, neo, exception_tester):
    exception_tester("", boosting_controller.boost, farm_token, 1, boosting_controller.minLockingPeriod(), {'from': neo})


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_farm_token(boosting_controller, farm_token, neo, amount, delta):
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
    assert boosting_controller.boosts(neo)[1] - (amount - math.floor((blockTimestamp_3 - boosting_controller.boosts(neo)[2]) * (amount - math.floor(amount / 2)) / (boosting_controller.boosts(neo)[3] - boosting_controller.boosts(neo)[2]))) <= 1
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((instant_value_3 + amount) * (blockTimestamp_3 - boosting_controller.boosts(neo)[2]) / 2) + math.floor((amount + instant_value_2) * (boosting_controller.boosts(neo)[2] - blockTimestamp_2) / 2) + previous_integral_neo) <= 1
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
    assert boosting_controller.boosts(neo)[1] - (amount - math.floor((blockTimestamp_4 - boosting_controller.boosts(neo)[2]) * (amount - math.floor(amount / 2)) / (boosting_controller.boosts(neo)[3] - boosting_controller.boosts(neo)[2]))) <= 1
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((instant_value_4 + instant_value_3) * (blockTimestamp_4 - blockTimestamp_3) / 2) + previous_integral_neo) <= 1
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
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((instant_value_5 + instant_value_5) * (blockTimestamp_5 - boosting_controller.boosts(neo)[3]) / 2) + math.floor((instant_value_5 + instant_value_4) * (boosting_controller.boosts(neo)[3] - blockTimestamp_4) / 2) + previous_integral_neo) <= 1
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
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((instant_value_6 + instant_value_6) * (blockTimestamp_6 - blockTimestamp_5) / 2) + previous_integral_neo) <= 1
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)

    # wait for some time (end of reduction + 3 * week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime + 3 * week)

    # unboost all tokens
    tx4 = boosting_controller.unboost(farm_token, {'from': neo})
    blockTimestamp_7 = brownie.chain.time()

    # check tx4 events
    assert tx4.return_value is None
    assert len(tx4.events) == 2
    assert tx4.events["Unboost"].values() == [farm_token, neo, amount]    

    assert boosting_controller.balances(farm_token, neo) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_7 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_7 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_7 = boosting_controller.lastBoostTimestampFor(neo)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == 0
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == 0
    assert boosting_controller.boosts(neo)[3] == 0
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((instant_value_6 + instant_value_6) * (blockTimestamp_7 - blockTimestamp_6) / 2) + previous_integral_neo) <= 1
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)
    previous_integral = boosting_controller.boostIntegral()

    # wait for some time
    brownie.chain.mine(1, brownie.chain.time() + week)
    blockTimestamp_8 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_8 >= boosting_controller.lastBoostTimestamp() + week
    assert blockTimestamp_8 >= boosting_controller.lastBoostTimestampFor(neo) + week
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == 0
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == 0
    assert boosting_controller.boosts(neo)[3] == 0
    assert boosting_controller.boostIntegralFor(neo) == previous_integral_neo
    assert boosting_controller.boostIntegral() == previous_integral


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_boosting_token(boosting_controller, boosting_token, neo, morpheus, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    initial_boost_integral = boosting_controller.boostIntegral()

    # boost with boosting_token 1st time
    boosting_token.transfer(morpheus, 5 * amount, {'from': neo})
    boosting_token.approve(boosting_controller, 5 * amount, {'from': morpheus})
    tx1 = boosting_controller.boost(boosting_token, amount, minLockTime, {'from': morpheus})
    blockTimestamp = brownie.chain.time()

    # check tx1 event
    assert tx1.return_value is None
    assert len(tx1.events) == 2
    assert tx1.events["Boost"].values() == [boosting_token, morpheus, amount]

    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert boosting_controller.boostIntegral() == 0 + initial_boost_integral
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller.lastBoostTimestamp()
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(morpheus) == 0
    assert boosting_controller.lastBoostTimestampFor(morpheus) == blockTimestamp

    # wait for some time (quater of warmup - delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 4 - delta)

    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert boosting_controller.boostIntegral() == 0 + initial_boost_integral
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() == 0    
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(morpheus) == 0
    assert boosting_controller.lastBoostTimestampFor(morpheus) == blockTimestamp

    # wait for some time (up to quater of warmup)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 4)

    tx2 = boosting_controller.commonBoostIntegral()
    tx3 = boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(morpheus)
    instant_value_1 = boosting_controller.boosts(morpheus)[1]
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[1] == amount * boosting_controller.boostingTokenRate() * (blockTimestamp_1 - blockTimestamp) / boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(morpheus) == (instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2
    assert tx2.return_value == boosting_controller.boostIntegral()
    assert tx3.return_value == boosting_controller.boostIntegralFor(morpheus)

    # wait for some time (up to half of warmup + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 2 + delta)

    tx2 = boosting_controller.commonBoostIntegral()
    tx3 = boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(morpheus)
    instant_value_2 = boosting_controller.boosts(morpheus)[1]
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[1] == amount * boosting_controller.boostingTokenRate() * (blockTimestamp_2 - blockTimestamp) / boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boostIntegralFor(morpheus) == math.floor((instant_value_2 + instant_value_1) * (blockTimestamp_2 - blockTimestamp_1) / 2) + math.floor((instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2)
    assert tx2.return_value == boosting_controller.boostIntegral()
    assert tx3.return_value == boosting_controller.boostIntegralFor(morpheus)
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)

    # wait for some time (end of warmup + quater of reduction)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime / 4)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_3 = brownie.chain.time()

    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_3 = boosting_controller.lastBoostTimestampFor(morpheus)
    instant_value_3 = boosting_controller.boosts(morpheus)[1]
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(morpheus)[1] - (amount * boosting_controller.boostingTokenRate() - math.floor((blockTimestamp_3 - boosting_controller.boosts(morpheus)[2]) * (amount * boosting_controller.boostingTokenRate() - math.floor(amount * boosting_controller.boostingTokenRate() / 2)) / (boosting_controller.boosts(morpheus)[3] - boosting_controller.boosts(morpheus)[2]))) <= 1
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((instant_value_3 + amount * boosting_controller.boostingTokenRate()) * (blockTimestamp_3 - boosting_controller.boosts(morpheus)[2]) / 2) + math.floor((amount * boosting_controller.boostingTokenRate() + instant_value_2) * (boosting_controller.boosts(morpheus)[2] - blockTimestamp_2) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)

    # wait for some time (end of warmup + 3/4 of reduction)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime * 3 / 4)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_4 = brownie.chain.time()

    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert blockTimestamp_4 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_4 = boosting_controller.lastBoostTimestampFor(morpheus)
    instant_value_4 = boosting_controller.boosts(morpheus)[1]
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(morpheus)[1] - (amount * boosting_controller.boostingTokenRate() - math.floor((blockTimestamp_4 - boosting_controller.boosts(morpheus)[2]) * (amount * boosting_controller.boostingTokenRate() - math.floor(amount * boosting_controller.boostingTokenRate() / 2)) / (boosting_controller.boosts(morpheus)[3] - boosting_controller.boosts(morpheus)[2]))) <= 1
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((instant_value_4 + instant_value_3) * (blockTimestamp_4 - blockTimestamp_3) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)

    # wait for some time (end of reduction + week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime + week)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_5 = brownie.chain.time()
    
    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert blockTimestamp_5 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_5 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_5 = boosting_controller.lastBoostTimestampFor(morpheus)
    instant_value_5 = boosting_controller.boosts(morpheus)[1]
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(morpheus)[1] == amount * boosting_controller.boostingTokenRate() - math.floor(amount * boosting_controller.boostingTokenRate() / 2)
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((instant_value_5 + instant_value_5) * (blockTimestamp_5 - boosting_controller.boosts(morpheus)[3]) / 2) + math.floor((instant_value_5 + instant_value_4) * (boosting_controller.boosts(morpheus)[3] - blockTimestamp_4) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)

    # wait for some time (end of reduction + 2 * week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime + 2 * week)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_6 = brownie.chain.time()
    
    assert boosting_controller.balances(boosting_token, morpheus) == amount
    assert boosting_controller.coinBalances(boosting_token) == amount
    assert blockTimestamp_6 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_6 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_6 = boosting_controller.lastBoostTimestampFor(morpheus)
    instant_value_6 = boosting_controller.boosts(morpheus)[1]
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount * boosting_controller.boostingTokenRate()
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + minLockTime
    assert boosting_controller.boosts(morpheus)[1] == amount * boosting_controller.boostingTokenRate() - math.floor(amount * boosting_controller.boostingTokenRate() / 2)
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((instant_value_6 + instant_value_6) * (blockTimestamp_6 - blockTimestamp_5) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)

    # wait for some time (end of reduction + 3 * week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + minLockTime + 3 * week)

    # unboost all tokens
    tx4 = boosting_controller.unboost(boosting_token, {'from': morpheus})
    blockTimestamp_7 = brownie.chain.time()

    # check tx4 events
    assert tx4.return_value is None
    assert len(tx4.events) == 2
    assert tx4.events["Unboost"].values() == [boosting_token, morpheus, amount]    

    assert boosting_controller.balances(boosting_token, morpheus) == 0
    assert boosting_controller.coinBalances(boosting_token) == 0
    assert blockTimestamp_7 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_7 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_7 = boosting_controller.lastBoostTimestampFor(morpheus)
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == 0
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == 0
    assert boosting_controller.boosts(morpheus)[3] == 0
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((instant_value_6 + instant_value_6) * (blockTimestamp_7 - blockTimestamp_6) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)
    previous_integral = boosting_controller.boostIntegral()

    # wait for some time
    brownie.chain.mine(1, brownie.chain.time() + week)
    blockTimestamp_8 = brownie.chain.time()

    assert boosting_controller.balances(boosting_token, morpheus) == 0
    assert boosting_controller.coinBalances(boosting_token) == 0
    assert blockTimestamp_8 >= boosting_controller.lastBoostTimestamp() + week
    assert blockTimestamp_8 >= boosting_controller.lastBoostTimestampFor(morpheus) + week
    assert boosting_controller.boostIntegral() == amount * boosting_controller.boostingTokenRate() * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == 0
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == 0
    assert boosting_controller.boosts(morpheus)[3] == 0
    assert boosting_controller.boostIntegralFor(morpheus) == previous_integral_morpheus
    assert boosting_controller.boostIntegral() == previous_integral
