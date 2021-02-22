import brownie, math
from brownie.test import given, strategy

day = 86_400
week = 7 * day

@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_update_on_reduction(boosting_controller, farm_token, neo, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    # boost with farm_token 1st time
    farm_token.approve(boosting_controller, amount, {'from': neo})
    boosting_controller.boost(farm_token, amount, 2 * minLockTime, {'from': neo})
    blockTimestamp = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert boosting_controller.boostIntegral() == 0
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller.lastBoostTimestamp()
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boostIntegralFor(neo) == 0
    assert boosting_controller.lastBoostTimestampFor(neo) == blockTimestamp

    # wait for some time (warmup + 1/4 of reduction + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime / 4 + delta)
    
    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(neo)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == amount
    assert boosting_controller.boosts(neo)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boosts(neo)[1] - (amount - math.floor((blockTimestamp_1 - boosting_controller.boosts(neo)[2]) * (amount - math.floor(amount / 2)) / (boosting_controller.boosts(neo)[3] - boosting_controller.boosts(neo)[2]))) <= 1
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((boosting_controller.boosts(neo)[1] + amount) * (blockTimestamp_1 - boosting_controller.boosts(neo)[2]) / 2) + math.floor(amount * boosting_controller.warmupTime() / 2)) <= 1

    with brownie.reverts("tokens are locked"):
        boosting_controller.unboost(farm_token, {'from': neo})

    # wait for some time (warmup + reduction + 1)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime + 1)

    # unboost all tokens
    boosting_controller.unboost(farm_token, {'from': neo})
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(neo)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == 0
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == 0
    assert boosting_controller.boosts(neo)[3] == 0
    assert boosting_controller.boostIntegralFor(neo) - (math.floor((amount + (amount - math.floor(amount / 2))) * (blockTimestamp_2 - (blockTimestamp + boosting_controller.warmupTime())) / 2) + math.floor(amount * boosting_controller.warmupTime() / 2)) <= 1
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)
    previous_integral = boosting_controller.boostIntegral()

    # wait for some time
    brownie.chain.mine(1, brownie.chain.time() + day)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(neo)
    blockTimestamp_3 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    assert boosting_controller.boosts(neo)[0] == 0
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == 0
    assert boosting_controller.boosts(neo)[3] == 0
    assert boosting_controller.boostIntegralFor(neo) == previous_integral_neo
    assert boosting_controller.boostIntegral() == previous_integral

@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_update_after_reduction(boosting_controller, farm_token, neo, morpheus, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    initial_boost_integral = boosting_controller.boostIntegral()

    # boost with farm_token 1st time
    farm_token.transfer(morpheus, amount, {'from': neo})
    farm_token.approve(boosting_controller, amount, {'from': morpheus})
    boosting_controller.boost(farm_token, amount, 2 * minLockTime, {'from': morpheus})
    blockTimestamp = brownie.chain.time()

    assert boosting_controller.balances(farm_token, morpheus) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert boosting_controller.boostIntegral() == initial_boost_integral
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller.lastBoostTimestamp()
    assert boosting_controller.boosts(morpheus)[0] == amount
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boostIntegralFor(morpheus) == 0
    assert boosting_controller.lastBoostTimestampFor(morpheus) == blockTimestamp

    # wait for some time (warmup + reduction + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime + delta)
    
    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, morpheus) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(morpheus)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == amount
    assert boosting_controller.boosts(morpheus)[1] == amount - math.floor(amount / 2)
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((amount - math.floor(amount / 2)) * (blockTimestamp_1 - boosting_controller.boosts(morpheus)[3])) + math.floor((amount + (amount - math.floor(amount / 2))) * (boosting_controller.boosts(morpheus)[3] - boosting_controller.boosts(morpheus)[2]) / 2) + math.floor(amount * boosting_controller.warmupTime() / 2)) <= 1

    # unboost all tokens
    boosting_controller.unboost(farm_token, {'from': morpheus})
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, morpheus) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(morpheus)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == 0
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == 0
    assert boosting_controller.boosts(morpheus)[3] == 0
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((amount - math.floor(amount / 2)) * (blockTimestamp_2 - boosting_controller.boosts(morpheus)[3])) + math.floor((amount + (amount - math.floor(amount / 2))) * (boosting_controller.boosts(morpheus)[3] - boosting_controller.boosts(morpheus)[2]) / 2) + math.floor(amount * boosting_controller.warmupTime() / 2)) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)
    previous_integral = boosting_controller.boostIntegral()

    # wait for some time
    brownie.chain.mine(1, brownie.chain.time() + day)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(morpheus)
    blockTimestamp_3 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, morpheus) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    assert boosting_controller.boosts(morpheus)[0] == 0
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == 0
    assert boosting_controller.boosts(morpheus)[3] == 0
    assert boosting_controller.boostIntegralFor(morpheus) == previous_integral_morpheus
    assert boosting_controller.boostIntegral() == previous_integral


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_update_on_warmup_and_after_reduction(boosting_controller, farm_token, neo, trinity, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    initial_boost_integral = boosting_controller.boostIntegral()

    # boost with farm_token 1st time
    farm_token.transfer(trinity, amount, {'from': neo})
    farm_token.approve(boosting_controller, amount, {'from': trinity})
    boosting_controller.boost(farm_token, amount, 2 * minLockTime, {'from': trinity})
    blockTimestamp = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert boosting_controller.boostIntegral() == initial_boost_integral
    assert blockTimestamp - boosting_controller.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller.lastBoostTimestamp()
    assert boosting_controller.boosts(trinity)[0] == amount
    assert boosting_controller.boosts(trinity)[1] == 0
    assert boosting_controller.boosts(trinity)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(trinity)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boostIntegralFor(trinity) == 0
    assert boosting_controller.lastBoostTimestampFor(trinity) == blockTimestamp

    # wait for some time (up to half of warmup + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 2 + delta)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(trinity)
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(trinity)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(trinity)[0] == amount
    assert boosting_controller.boosts(trinity)[1] == amount * (blockTimestamp_1 - blockTimestamp) / boosting_controller.warmupTime()
    assert boosting_controller.boosts(trinity)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(trinity)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boostIntegralFor(trinity) == math.floor(boosting_controller.boosts(trinity)[1] * (blockTimestamp_1 - blockTimestamp) / 2)

    # wait for some time (warmup + reduction + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime + delta)
    
    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(trinity)
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == amount
    assert boosting_controller.coinBalances(farm_token) == amount
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(trinity)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(trinity)[0] == amount
    assert boosting_controller.boosts(trinity)[1] == amount - math.floor(amount / 2)
    assert boosting_controller.boosts(trinity)[2] == blockTimestamp + boosting_controller.warmupTime()
    assert boosting_controller.boosts(trinity)[3] == blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime
    assert boosting_controller.boostIntegralFor(trinity) - (math.floor((amount - math.floor(amount / 2)) * (blockTimestamp_2 - boosting_controller.boosts(trinity)[3])) + math.floor((amount + (amount - math.floor(amount / 2))) * (boosting_controller.boosts(trinity)[3] - boosting_controller.boosts(trinity)[2]) / 2) + math.floor(amount * boosting_controller.warmupTime() / 2)) <= 1

    # unboost all tokens
    boosting_controller.unboost(farm_token, {'from': trinity})
    blockTimestamp_3 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - boosting_controller.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_3 = boosting_controller.lastBoostTimestampFor(trinity)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(trinity)[0] == 0
    assert boosting_controller.boosts(trinity)[1] == 0
    assert boosting_controller.boosts(trinity)[2] == 0
    assert boosting_controller.boosts(trinity)[3] == 0
    assert boosting_controller.boostIntegralFor(trinity) - (math.floor((amount - math.floor(amount / 2)) * (blockTimestamp_3 - boosting_controller.boosts(trinity)[3])) + math.floor((amount + (amount - math.floor(amount / 2))) * (boosting_controller.boosts(trinity)[3] - boosting_controller.boosts(trinity)[2]) / 2) + math.floor(amount * boosting_controller.warmupTime() / 2)) <= 1
    previous_integral_trinity = boosting_controller.boostIntegralFor(trinity)
    previous_integral = boosting_controller.boostIntegral()

    # wait for some time
    brownie.chain.mine(1, brownie.chain.time() + day)

    boosting_controller.commonBoostIntegral()
    boosting_controller.accountBoostIntegral(trinity)
    blockTimestamp_4 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_4 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - boosting_controller.lastBoostTimestampFor(trinity) <= 1
    assert boosting_controller.boosts(trinity)[0] == 0
    assert boosting_controller.boosts(trinity)[1] == 0
    assert boosting_controller.boosts(trinity)[2] == 0
    assert boosting_controller.boosts(trinity)[3] == 0
    assert boosting_controller.boostIntegralFor(trinity) == previous_integral_trinity
    assert boosting_controller.boostIntegral() == previous_integral
