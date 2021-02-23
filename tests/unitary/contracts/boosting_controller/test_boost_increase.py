import math
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_increase_on_warmup(boosting_controller_mocked, farm_token, deployer, amount, week, delta, chain):
    minLockTime = 2 * week
    warmupTime = 2 * week

    # boost with farm_token 1st time
    farm_token.approve(boosting_controller_mocked,
                       3 * amount, {'from': deployer})
    boosting_controller_mocked.boost(
        farm_token, amount, 2 * minLockTime, {'from': deployer})
    blockTimestamp = chain.time()

    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert boosting_controller_mocked.boostIntegral() == 0
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + 2 * minLockTime
    assert boosting_controller_mocked.boostIntegralFor(deployer) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        deployer) == blockTimestamp

    # wait for some time (1/2 of warmup + delta)
    chain.mine(1, blockTimestamp + warmupTime / 2 + delta)

    # boost one more time to increase current boost
    boosting_controller_mocked.boost(
        farm_token, 2 * amount, 3 * minLockTime, {'from': deployer})
    blockTimestamp_1 = chain.time()

    assert boosting_controller_mocked.balances(
        farm_token, deployer) == 3 * amount
    assert boosting_controller_mocked.coinBalances(farm_token) == 3 * amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == 3 * amount
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp_1 + warmupTime
    assert boosting_controller_mocked.boosts(deployer)[3] == max(
        blockTimestamp + warmupTime + 5 * minLockTime, blockTimestamp_1 + warmupTime + 3 * minLockTime)
    assert boosting_controller_mocked.boosts(
        deployer)[1] == amount * (blockTimestamp_1 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boostIntegralFor(deployer) == (
        boosting_controller_mocked.boosts(deployer)[1] + 0) * (blockTimestamp_1 - blockTimestamp) / 2
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    previous_integral = boosting_controller_mocked.boostIntegral()
    previous_deployer_target = boosting_controller_mocked.boosts(deployer)[0]
    previous_deployer_instant = boosting_controller_mocked.boosts(deployer)[1]
    previous_deployer_warmupTime = boosting_controller_mocked.boosts(deployer)[
        2]
    previous_deployer_finishTime = boosting_controller_mocked.boosts(deployer)[
        3]

    # wait for some time (end of new reduction + delta)
    chain.mine(1, boosting_controller_mocked.boosts(deployer)[3] + delta)

    # unboost all tokens
    boosting_controller_mocked.unboost(farm_token, {'from': deployer})
    blockTimestamp_2 = chain.time()

    assert boosting_controller_mocked.balances(farm_token, deployer) == 0
    assert boosting_controller_mocked.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    assert boosting_controller_mocked.boostIntegral() == previous_deployer_target * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp_1) + previous_integral
    assert boosting_controller_mocked.boosts(deployer)[0] == 0
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(deployer)[2] == 0
    assert boosting_controller_mocked.boosts(deployer)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(deployer) == math.floor(math.floor(previous_deployer_target / 2) * (blockTimestamp_2 - previous_deployer_finishTime) +
                                                                               math.floor((previous_deployer_target + math.floor(previous_deployer_target / 2)) * (previous_deployer_finishTime - previous_deployer_warmupTime) / 2) +
                                                                               math.floor((previous_deployer_instant + previous_deployer_target) * (previous_deployer_warmupTime - blockTimestamp_1) / 2) + previous_integral_deployer)


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_increase_on_reduction(boosting_controller_mocked, farm_token, deployer, morpheus, amount, delta, week, chain):
    minLockTime = 2 * week
    warmupTime = 2 * week

    initial_boost_integral = boosting_controller_mocked.boostIntegral()

    # boost with farm_token 1st time
    farm_token.transfer(morpheus, 3 * amount, {'from': deployer})
    farm_token.approve(boosting_controller_mocked,
                       3 * amount, {'from': morpheus})
    boosting_controller_mocked.boost(
        farm_token, amount, 2 * minLockTime, {'from': morpheus})
    blockTimestamp = chain.time()

    assert boosting_controller_mocked.balances(farm_token, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert boosting_controller_mocked.boostIntegral() == initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + 2 * minLockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) == blockTimestamp

    # wait for some time (warmup + 3/4 of reduction + delta)
    chain.mine(1, blockTimestamp + warmupTime +
               2 * minLockTime * 3 / 4 + delta)

    # boost one more time to increase current boost
    boosting_controller_mocked.boost(
        farm_token, 2 * amount, 3 * minLockTime, {'from': morpheus})
    blockTimestamp_1 = chain.time()

    assert boosting_controller_mocked.balances(
        farm_token, morpheus) == 3 * amount
    assert boosting_controller_mocked.coinBalances(farm_token) == 3 * amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == 3 * amount
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp_1 + warmupTime
    assert boosting_controller_mocked.boosts(morpheus)[3] == max(
        blockTimestamp + warmupTime + 5 * minLockTime, blockTimestamp_1 + warmupTime + 3 * minLockTime)
    assert boosting_controller_mocked.boosts(morpheus)[1] - (amount - math.floor((blockTimestamp_1 - (blockTimestamp + warmupTime)) * (
        amount - math.floor(amount / 2)) / ((blockTimestamp + warmupTime + 2 * minLockTime) - (blockTimestamp + warmupTime)))) <= 1
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((amount + boosting_controller_mocked.boosts(
        morpheus)[1]) * (blockTimestamp_1 - (blockTimestamp + warmupTime)) / 2) + amount * warmupTime / 2) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    previous_integral = boosting_controller_mocked.boostIntegral()
    previous_morpheus_target = boosting_controller_mocked.boosts(morpheus)[0]
    previous_morpheus_instant = boosting_controller_mocked.boosts(morpheus)[1]
    previous_morpheus_warmupTime = boosting_controller_mocked.boosts(morpheus)[
        2]
    previous_morpheus_finishTime = boosting_controller_mocked.boosts(morpheus)[
        3]

    # wait for some time (end of new reduction + delta)
    chain.mine(1, boosting_controller_mocked.boosts(morpheus)[3] + delta)

    # unboost all tokens
    boosting_controller_mocked.unboost(farm_token, {'from': morpheus})
    blockTimestamp_2 = chain.time()

    assert boosting_controller_mocked.balances(farm_token, morpheus) == 0
    assert boosting_controller_mocked.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    assert boosting_controller_mocked.boostIntegral() == previous_morpheus_target * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp_1) + previous_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == 0
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(morpheus)[2] == 0
    assert boosting_controller_mocked.boosts(morpheus)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == math.floor(math.floor(previous_morpheus_target / 2) * (blockTimestamp_2 - previous_morpheus_finishTime) +
                                                                               math.floor((previous_morpheus_target + math.floor(previous_morpheus_target / 2)) * (previous_morpheus_finishTime - previous_morpheus_warmupTime) / 2) +
                                                                               math.floor((previous_morpheus_instant + previous_morpheus_target) * (previous_morpheus_warmupTime - blockTimestamp_1) / 2) + previous_integral_morpheus)


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_increase_after_reduction(boosting_controller_mocked, farm_token, deployer, trinity, amount, delta, week, chain):
    minLockTime = 2 * week
    warmupTime = 2 * week

    initial_boost_integral = boosting_controller_mocked.boostIntegral()

    # boost with farm_token 1st time
    farm_token.transfer(trinity, 3 * amount, {'from': deployer})
    farm_token.approve(boosting_controller_mocked,
                       3 * amount, {'from': trinity})
    boosting_controller_mocked.boost(
        farm_token, amount, 2 * minLockTime, {'from': trinity})
    blockTimestamp = chain.time()

    assert boosting_controller_mocked.balances(farm_token, trinity) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert boosting_controller_mocked.boostIntegral() == initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(trinity)[0] == amount
    assert boosting_controller_mocked.boosts(trinity)[1] == 0
    assert boosting_controller_mocked.boosts(
        trinity)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        trinity)[3] == blockTimestamp + warmupTime + 2 * minLockTime
    assert boosting_controller_mocked.boostIntegralFor(trinity) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        trinity) == blockTimestamp

    # wait for some time (warmup + end of reduction + week)
    chain.mine(1, blockTimestamp + warmupTime + 2 * minLockTime + week)

    # boost one more time to increase current boost
    boosting_controller_mocked.boost(
        farm_token, 2 * amount, 3 * minLockTime, {'from': trinity})
    blockTimestamp_1 = chain.time()

    assert boosting_controller_mocked.balances(
        farm_token, trinity) == 3 * amount
    assert boosting_controller_mocked.coinBalances(farm_token) == 3 * amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        trinity)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(trinity)[0] == 3 * amount
    assert boosting_controller_mocked.boosts(
        trinity)[2] == blockTimestamp_1 + warmupTime
    assert boosting_controller_mocked.boosts(trinity)[3] == max(
        blockTimestamp + warmupTime + 5 * minLockTime, blockTimestamp_1 + warmupTime + 3 * minLockTime)
    # (amount - math.floor((blockTimestamp_1 - (blockTimestamp + warmupTime)) * (amount - math.floor(amount / 2)) / ((blockTimestamp + warmupTime + 2 * minLockTime) - (blockTimestamp + warmupTime)))) <= 1
    assert boosting_controller_mocked.boosts(
        trinity)[1] == math.floor(amount - math.floor(amount / 2))
    assert boosting_controller_mocked.boostIntegralFor(trinity) - (math.floor((amount + boosting_controller_mocked.boosts(
        trinity)[1]) * (blockTimestamp_1 - (blockTimestamp + warmupTime)) / 2) + amount * warmupTime / 2) <= 1
    previous_integral_trinity = boosting_controller_mocked.boostIntegralFor(
        trinity)
    previous_integral = boosting_controller_mocked.boostIntegral()
    previous_trinity_target = boosting_controller_mocked.boosts(trinity)[0]
    previous_trinity_instant = boosting_controller_mocked.boosts(trinity)[1]
    previous_trinity_warmupTime = boosting_controller_mocked.boosts(trinity)[2]
    previous_trinity_finishTime = boosting_controller_mocked.boosts(trinity)[3]

    # wait for some time (end of new reduction + delta)
    chain.mine(1, boosting_controller_mocked.boosts(trinity)[3] + delta)

    # unboost all tokens
    boosting_controller_mocked.unboost(farm_token, {'from': trinity})
    blockTimestamp_2 = chain.time()

    assert boosting_controller_mocked.balances(farm_token, trinity) == 0
    assert boosting_controller_mocked.coinBalances(farm_token) == 0
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        trinity)
    assert boosting_controller_mocked.boostIntegral() == previous_trinity_target * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp_1) + previous_integral
    assert boosting_controller_mocked.boosts(trinity)[0] == 0
    assert boosting_controller_mocked.boosts(trinity)[1] == 0
    assert boosting_controller_mocked.boosts(trinity)[2] == 0
    assert boosting_controller_mocked.boosts(trinity)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(trinity) == math.floor(math.floor(previous_trinity_target / 2) * (blockTimestamp_2 - previous_trinity_finishTime) +
                                                                              math.floor((previous_trinity_target + math.floor(previous_trinity_target / 2)) * (previous_trinity_finishTime - previous_trinity_warmupTime) / 2) +
                                                                              math.floor((previous_trinity_instant + previous_trinity_target) * (previous_trinity_warmupTime - blockTimestamp_1) / 2) + previous_integral_trinity)
