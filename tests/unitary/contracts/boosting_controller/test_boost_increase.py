import brownie, math
from brownie.test import given, strategy

day = 86_400
week = 7 * day

@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_increase_on_warmup(boosting_controller, farm_token, neo, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    # boost with farm_token 1st time
    farm_token.approve(boosting_controller, 3 * amount, {'from': neo})
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

    # wait for some time (1/2 of warmup + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() / 2 + delta)
    
    # boost one more time to increase current boost
    boosting_controller.boost(farm_token, 2 * amount, 3 * minLockTime, {'from': neo})
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == 3 * amount
    assert boosting_controller.coinBalances(farm_token) == 3 * amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(neo)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller.boosts(neo)[0] == 3 * amount
    assert boosting_controller.boosts(neo)[2] == blockTimestamp_1 + boosting_controller.warmupTime()
    assert boosting_controller.boosts(neo)[3] == max(blockTimestamp + boosting_controller.warmupTime() + 5 * minLockTime, blockTimestamp_1 + boosting_controller.warmupTime() + 3 * minLockTime)
    assert boosting_controller.boosts(neo)[1] == amount * (blockTimestamp_1 - blockTimestamp) / boosting_controller.warmupTime()
    assert boosting_controller.boostIntegralFor(neo)  == (boosting_controller.boosts(neo)[1] + 0) * (blockTimestamp_1 - blockTimestamp) / 2
    previous_integral_neo = boosting_controller.boostIntegralFor(neo)
    previous_integral = boosting_controller.boostIntegral()
    previous_neo_target = boosting_controller.boosts(neo)[0]
    previous_neo_instant = boosting_controller.boosts(neo)[1]
    previous_neo_warmupTime = boosting_controller.boosts(neo)[2]
    previous_neo_finishTime = boosting_controller.boosts(neo)[3]

    # wait for some time (end of new reduction + delta)
    brownie.chain.mine(1, boosting_controller.boosts(neo)[3] + delta)

    # unboost all tokens
    boosting_controller.unboost(farm_token, {'from': neo})
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, neo) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(neo) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(neo)
    assert boosting_controller.boostIntegral() == previous_neo_target * (boosting_controller.lastBoostTimestamp() - blockTimestamp_1) + previous_integral
    assert boosting_controller.boosts(neo)[0] == 0
    assert boosting_controller.boosts(neo)[1] == 0
    assert boosting_controller.boosts(neo)[2] == 0
    assert boosting_controller.boosts(neo)[3] == 0
    assert boosting_controller.boostIntegralFor(neo) == math.floor(math.floor(previous_neo_target / 2) * (blockTimestamp_2 - previous_neo_finishTime) + \
    math.floor((previous_neo_target + math.floor(previous_neo_target / 2)) * (previous_neo_finishTime - previous_neo_warmupTime) / 2) + \
    math.floor((previous_neo_instant + previous_neo_target) * (previous_neo_warmupTime - blockTimestamp_1) / 2) + previous_integral_neo)


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_increase_on_reduction(boosting_controller, farm_token, neo, morpheus, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    initial_boost_integral = boosting_controller.boostIntegral()

    # boost with farm_token 1st time
    farm_token.transfer(morpheus, 3 * amount, {'from': neo})
    farm_token.approve(boosting_controller, 3 * amount, {'from': morpheus})
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

    # wait for some time (warmup + 3/4 of reduction + delta)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime * 3 / 4 + delta)
    
    # boost one more time to increase current boost
    boosting_controller.boost(farm_token, 2 * amount, 3 * minLockTime, {'from': morpheus})
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, morpheus) == 3 * amount
    assert boosting_controller.coinBalances(farm_token) == 3 * amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(morpheus)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(morpheus)[0] == 3 * amount
    assert boosting_controller.boosts(morpheus)[2] == blockTimestamp_1 + boosting_controller.warmupTime()
    assert boosting_controller.boosts(morpheus)[3] == max(blockTimestamp + boosting_controller.warmupTime() + 5 * minLockTime, blockTimestamp_1 + boosting_controller.warmupTime() + 3 * minLockTime)
    assert boosting_controller.boosts(morpheus)[1] - (amount - math.floor((blockTimestamp_1 - (blockTimestamp + boosting_controller.warmupTime())) * (amount - math.floor(amount / 2)) / ((blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime) - (blockTimestamp + boosting_controller.warmupTime())))) <= 1
    assert boosting_controller.boostIntegralFor(morpheus) - (math.floor((amount + boosting_controller.boosts(morpheus)[1]) * (blockTimestamp_1 - (blockTimestamp + boosting_controller.warmupTime())) / 2) + amount * boosting_controller.warmupTime() / 2) <= 1
    previous_integral_morpheus = boosting_controller.boostIntegralFor(morpheus)
    previous_integral = boosting_controller.boostIntegral()
    previous_morpheus_target = boosting_controller.boosts(morpheus)[0]
    previous_morpheus_instant = boosting_controller.boosts(morpheus)[1]
    previous_morpheus_warmupTime = boosting_controller.boosts(morpheus)[2]
    previous_morpheus_finishTime = boosting_controller.boosts(morpheus)[3]

    # wait for some time (end of new reduction + delta)
    brownie.chain.mine(1, boosting_controller.boosts(morpheus)[3] + delta)

    # unboost all tokens
    boosting_controller.unboost(farm_token, {'from': morpheus})
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, morpheus) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(morpheus)
    assert boosting_controller.boostIntegral() == previous_morpheus_target * (boosting_controller.lastBoostTimestamp() - blockTimestamp_1) + previous_integral
    assert boosting_controller.boosts(morpheus)[0] == 0
    assert boosting_controller.boosts(morpheus)[1] == 0
    assert boosting_controller.boosts(morpheus)[2] == 0
    assert boosting_controller.boosts(morpheus)[3] == 0
    assert boosting_controller.boostIntegralFor(morpheus) == math.floor(math.floor(previous_morpheus_target / 2) * (blockTimestamp_2 - previous_morpheus_finishTime) + \
    math.floor((previous_morpheus_target + math.floor(previous_morpheus_target / 2)) * (previous_morpheus_finishTime - previous_morpheus_warmupTime) / 2) + \
    math.floor((previous_morpheus_instant + previous_morpheus_target) * (previous_morpheus_warmupTime - blockTimestamp_1) / 2) + previous_integral_morpheus)


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_increase_after_reduction(boosting_controller, farm_token, neo, trinity, amount, delta):
    minLockTime = boosting_controller.minLockingPeriod()

    initial_boost_integral = boosting_controller.boostIntegral()

    # boost with farm_token 1st time
    farm_token.transfer(trinity, 3 * amount, {'from': neo})
    farm_token.approve(boosting_controller, 3 * amount, {'from': trinity})
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

    # wait for some time (warmup + end of reduction + week)
    brownie.chain.mine(1, blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime + week)
    
    # boost one more time to increase current boost
    boosting_controller.boost(farm_token, 2 * amount, 3 * minLockTime, {'from': trinity})
    blockTimestamp_1 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == 3 * amount
    assert boosting_controller.coinBalances(farm_token) == 3 * amount
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - boosting_controller.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_1 = boosting_controller.lastBoostTimestampFor(trinity)
    assert boosting_controller.boostIntegral() == amount * (boosting_controller.lastBoostTimestamp() - blockTimestamp) + initial_boost_integral
    assert boosting_controller.boosts(trinity)[0] == 3 * amount
    assert boosting_controller.boosts(trinity)[2] == blockTimestamp_1 + boosting_controller.warmupTime()
    assert boosting_controller.boosts(trinity)[3] == max(blockTimestamp + boosting_controller.warmupTime() + 5 * minLockTime, blockTimestamp_1 + boosting_controller.warmupTime() + 3 * minLockTime)
    assert boosting_controller.boosts(trinity)[1] == math.floor(amount - math.floor(amount / 2)) #(amount - math.floor((blockTimestamp_1 - (blockTimestamp + boosting_controller.warmupTime())) * (amount - math.floor(amount / 2)) / ((blockTimestamp + boosting_controller.warmupTime() + 2 * minLockTime) - (blockTimestamp + boosting_controller.warmupTime())))) <= 1
    assert boosting_controller.boostIntegralFor(trinity) - (math.floor((amount + boosting_controller.boosts(trinity)[1]) * (blockTimestamp_1 - (blockTimestamp + boosting_controller.warmupTime())) / 2) + amount * boosting_controller.warmupTime() / 2) <= 1
    previous_integral_trinity = boosting_controller.boostIntegralFor(trinity)
    previous_integral = boosting_controller.boostIntegral()
    previous_trinity_target = boosting_controller.boosts(trinity)[0]
    previous_trinity_instant = boosting_controller.boosts(trinity)[1]
    previous_trinity_warmupTime = boosting_controller.boosts(trinity)[2]
    previous_trinity_finishTime = boosting_controller.boosts(trinity)[3]

    # wait for some time (end of new reduction + delta)
    brownie.chain.mine(1, boosting_controller.boosts(trinity)[3] + delta)

    # unboost all tokens
    boosting_controller.unboost(farm_token, {'from': trinity})
    blockTimestamp_2 = brownie.chain.time()

    assert boosting_controller.balances(farm_token, trinity) == 0
    assert boosting_controller.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - boosting_controller.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_2 = boosting_controller.lastBoostTimestampFor(trinity)
    assert boosting_controller.boostIntegral() == previous_trinity_target * (boosting_controller.lastBoostTimestamp() - blockTimestamp_1) + previous_integral
    assert boosting_controller.boosts(trinity)[0] == 0
    assert boosting_controller.boosts(trinity)[1] == 0
    assert boosting_controller.boosts(trinity)[2] == 0
    assert boosting_controller.boosts(trinity)[3] == 0
    assert boosting_controller.boostIntegralFor(trinity) == math.floor(math.floor(previous_trinity_target / 2) * (blockTimestamp_2 - previous_trinity_finishTime) + \
    math.floor((previous_trinity_target + math.floor(previous_trinity_target / 2)) * (previous_trinity_finishTime - previous_trinity_warmupTime) / 2) + \
    math.floor((previous_trinity_instant + previous_trinity_target) * (previous_trinity_warmupTime - blockTimestamp_1) / 2) + previous_integral_trinity)
