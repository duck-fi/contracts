import math
from brownie.test import given, strategy


def test_boost_wrong_token(boosting_controller_mocked, usdn_token, deployer, exception_tester, week):
    exception_tester("invalid coin", boosting_controller_mocked.boost,
                     usdn_token, 1, 2 * week, {'from': deployer})


def test_boost_short_locktime(boosting_controller_mocked, farm_token, deployer, exception_tester):
    assert boosting_controller_mocked.availableToUnboost(
        farm_token, deployer) == 0
    exception_tester("locktime is too short",
                     boosting_controller_mocked.boost, farm_token, 1, 1, {'from': deployer})


def test_boost_farm_token_not_approved(boosting_controller_mocked, farm_token, deployer, exception_tester, week):
    assert boosting_controller_mocked.availableToUnboost(
        farm_token, deployer) == 0
    exception_tester("", boosting_controller_mocked.boost, farm_token,
                     1, 2 * week, {'from': deployer})


@given(amount=strategy('uint256', min_value=10 ** 10, max_value=10 ** 13), delta=strategy('uint256', min_value=8_640, max_value=86_400 * 3))
def test_boost_farm_token(boosting_controller_mocked, farm_token, deployer, amount, delta, week, chain):
    minLockTime = 2 * week
    warmupTime = 2 * week
    # boost with farm_token 1st time
    farm_token.approve(boosting_controller_mocked,
                       5 * amount, {'from': deployer})
    assert boosting_controller_mocked.availableToUnboost(
        farm_token, deployer) == 0
    tx1 = boosting_controller_mocked.boost(
        farm_token, amount, minLockTime, {'from': deployer})
    assert boosting_controller_mocked.availableToUnboost(
        farm_token, deployer) == 0
    blockTimestamp = chain.time()
    # check tx1 event
    assert tx1.return_value is None
    assert len(tx1.events) == 2
    assert tx1.events["Boost"].values() == [farm_token, deployer, amount]
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
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(deployer) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        deployer) == blockTimestamp
    # wait for some time (quater of warmup - delta)
    chain.mine(1, blockTimestamp + warmupTime / 4 - delta)
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert boosting_controller_mocked.boostIntegral() == 0
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() == 0
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(deployer) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        deployer) == blockTimestamp
    # wait for some time (up to quater of warmup)
    chain.mine(1, blockTimestamp + warmupTime / 4)
    tx2 = boosting_controller_mocked.updateBoostIntegral()
    tx3 = boosting_controller_mocked.accountBoostIntegral(deployer)
    blockTimestamp_1 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    instant_value_1 = boosting_controller_mocked.boosts(deployer)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(deployer)[
        1] == amount * (blockTimestamp_1 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(deployer) == (
        instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2
    assert tx2.return_value == boosting_controller_mocked.boostIntegral()
    assert tx3.return_value == boosting_controller_mocked.boostIntegralFor(
        deployer)
    # wait for some time (up to half of warmup + delta)
    chain.mine(1, blockTimestamp +
               warmupTime / 2 + delta)
    tx2 = boosting_controller_mocked.updateBoostIntegral()
    tx3 = boosting_controller_mocked.accountBoostIntegral(deployer)
    blockTimestamp_2 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    instant_value_2 = boosting_controller_mocked.boosts(deployer)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(deployer)[
        1] == amount * (blockTimestamp_2 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(deployer) == math.floor((instant_value_2 + instant_value_1) * (
        blockTimestamp_2 - blockTimestamp_1) / 2) + math.floor((instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2)
    assert tx2.return_value == boosting_controller_mocked.boostIntegral()
    assert tx3.return_value == boosting_controller_mocked.boostIntegralFor(
        deployer)
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    # wait for some time (end of warmup + quater of reduction)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime / 4)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(deployer)
    blockTimestamp_3 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert blockTimestamp_3 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_3 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    instant_value_3 = boosting_controller_mocked.boosts(deployer)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(deployer)[1] - (amount - math.floor((blockTimestamp_3 - boosting_controller_mocked.boosts(deployer)[2]) * (
        amount - math.floor(amount / 2)) / (boosting_controller_mocked.boosts(deployer)[3] - boosting_controller_mocked.boosts(deployer)[2]))) <= 1
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor((instant_value_3 + amount) * (blockTimestamp_3 - boosting_controller_mocked.boosts(deployer)[
        2]) / 2) + math.floor((amount + instant_value_2) * (boosting_controller_mocked.boosts(deployer)[2] - blockTimestamp_2) / 2) + previous_integral_deployer) <= 1
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    # wait for some time (end of warmup + 3/4 of reduction)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime * 3 / 4)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(deployer)
    blockTimestamp_4 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert blockTimestamp_4 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_4 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    instant_value_4 = boosting_controller_mocked.boosts(deployer)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(deployer)[1] - (amount - math.floor((blockTimestamp_4 - boosting_controller_mocked.boosts(deployer)[2]) * (
        amount - math.floor(amount / 2)) / (boosting_controller_mocked.boosts(deployer)[3] - boosting_controller_mocked.boosts(deployer)[2]))) <= 1
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor((instant_value_4 + instant_value_3) * (
        blockTimestamp_4 - blockTimestamp_3) / 2) + previous_integral_deployer) <= 1
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    # wait for some time (end of reduction + week)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime + week)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(deployer)
    blockTimestamp_5 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert blockTimestamp_5 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_5 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_5 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    instant_value_5 = boosting_controller_mocked.boosts(deployer)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(
        deployer)[1] == amount - math.floor(amount / 2)
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor((instant_value_5 + instant_value_5) * (blockTimestamp_5 - boosting_controller_mocked.boosts(deployer)[
        3]) / 2) + math.floor((instant_value_5 + instant_value_4) * (boosting_controller_mocked.boosts(deployer)[3] - blockTimestamp_4) / 2) + previous_integral_deployer) <= 1
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    # wait for some time (end of reduction + 2 * week)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime + 2 * week)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(deployer)
    blockTimestamp_6 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == amount
    assert boosting_controller_mocked.coinBalances(farm_token) == amount
    assert blockTimestamp_6 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_6 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_6 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    instant_value_6 = boosting_controller_mocked.boosts(deployer)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(
        deployer)[1] == amount - math.floor(amount / 2)
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor((instant_value_6 + instant_value_6) * (
        blockTimestamp_6 - blockTimestamp_5) / 2) + previous_integral_deployer) <= 1
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    # wait for some time (end of reduction + 3 * week)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime + 3 * week)
    # unboost all tokens
    tx4 = boosting_controller_mocked.unboost(farm_token, {'from': deployer})
    blockTimestamp_7 = chain.time()
    # check tx4 events
    assert tx4.return_value is None
    assert len(tx4.events) == 2
    assert tx4.events["Unboost"].values() == [farm_token, deployer, amount]
    assert boosting_controller_mocked.balances(farm_token, deployer) == 0
    assert boosting_controller_mocked.coinBalances(farm_token) == 0
    assert blockTimestamp_7 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_7 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_7 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == 0
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(deployer)[2] == 0
    assert boosting_controller_mocked.boosts(deployer)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor((instant_value_6 + instant_value_6) * (
        blockTimestamp_7 - blockTimestamp_6) / 2) + previous_integral_deployer) <= 1
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    previous_integral = boosting_controller_mocked.boostIntegral()
    # wait for some time
    chain.mine(1, chain.time() + week)
    blockTimestamp_8 = chain.time()
    assert boosting_controller_mocked.balances(farm_token, deployer) == 0
    assert boosting_controller_mocked.coinBalances(farm_token) == 0
    assert blockTimestamp_8 >= boosting_controller_mocked.lastBoostTimestamp() + \
        week
    assert blockTimestamp_8 >= boosting_controller_mocked.lastBoostTimestampFor(
        deployer) + week
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == 0
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(deployer)[2] == 0
    assert boosting_controller_mocked.boosts(deployer)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(
        deployer) == previous_integral_deployer
    assert boosting_controller_mocked.boostIntegral() == previous_integral


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_boosting_token(boosting_controller_mocked, boosting_token_mocked, deployer, morpheus, amount, delta, chain, week):
    minLockTime = 2 * week
    warmupTime = 2 * week
    boostTokenRate = 2
    initial_boost_integral = boosting_controller_mocked.boostIntegral()
    # boost with boosting_token 1st time
    boosting_token_mocked.mint(morpheus, 5 * amount, {'from': deployer})
    boosting_token_mocked.approve(boosting_controller_mocked,
                                  5 * amount, {'from': morpheus})
    tx1 = boosting_controller_mocked.boost(
        boosting_token_mocked, amount, minLockTime, {'from': morpheus})
    blockTimestamp = chain.time()
    # check tx1 event
    assert tx1.return_value is None
    assert len(tx1.events) == 2
    assert tx1.events["Boost"].values(
    ) == [boosting_token_mocked, morpheus, amount]
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert boosting_controller_mocked.boostIntegral() == 0 + initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) == blockTimestamp
    # wait for some time (quater of warmup - delta)
    chain.mine(1, blockTimestamp +
               warmupTime / 4 - delta)
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert boosting_controller_mocked.boostIntegral() == 0 + initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) == blockTimestamp
    # wait for some time (up to quater of warmup)
    chain.mine(1, blockTimestamp + warmupTime / 4)
    tx2 = boosting_controller_mocked.updateBoostIntegral()
    tx3 = boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_1 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_1 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(morpheus)[
        1] == amount * boostTokenRate * (blockTimestamp_1 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == (
        instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2
    assert tx2.return_value == boosting_controller_mocked.boostIntegral()
    assert tx3.return_value == boosting_controller_mocked.boostIntegralFor(
        morpheus)
    # wait for some time (up to half of warmup + delta)
    chain.mine(1, blockTimestamp +
               warmupTime / 2 + delta)
    tx2 = boosting_controller_mocked.updateBoostIntegral()
    tx3 = boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_2 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_2 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(morpheus)[
        1] == amount * boostTokenRate * (blockTimestamp_2 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == math.floor((instant_value_2 + instant_value_1) * (
        blockTimestamp_2 - blockTimestamp_1) / 2) + math.floor((instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2)
    assert tx2.return_value == boosting_controller_mocked.boostIntegral()
    assert tx3.return_value == boosting_controller_mocked.boostIntegralFor(
        morpheus)
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    # wait for some time (end of warmup + quater of reduction)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime / 4)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_3 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert blockTimestamp_3 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_3 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_3 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(morpheus)[1] - (amount * boostTokenRate - math.floor((blockTimestamp_3 - boosting_controller_mocked.boosts(morpheus)[2]) * (
        amount * boostTokenRate - math.floor(amount * boostTokenRate / 2)) / (boosting_controller_mocked.boosts(morpheus)[3] - boosting_controller_mocked.boosts(morpheus)[2]))) <= 1
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_3 + amount * boostTokenRate) * (blockTimestamp_3 - boosting_controller_mocked.boosts(morpheus)[
        2]) / 2) + math.floor((amount * boostTokenRate + instant_value_2) * (boosting_controller_mocked.boosts(morpheus)[2] - blockTimestamp_2) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    # wait for some time (end of warmup + 3/4 of reduction)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime * 3 / 4)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_4 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert blockTimestamp_4 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_4 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_4 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(morpheus)[1] - (amount * boostTokenRate - math.floor((blockTimestamp_4 - boosting_controller_mocked.boosts(morpheus)[2]) * (
        amount * boostTokenRate - math.floor(amount * boostTokenRate / 2)) / (boosting_controller_mocked.boosts(morpheus)[3] - boosting_controller_mocked.boosts(morpheus)[2]))) <= 1
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_4 + instant_value_3) * (
        blockTimestamp_4 - blockTimestamp_3) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    # wait for some time (end of reduction + week)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime + week)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_5 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert blockTimestamp_5 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_5 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_5 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_5 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(
        morpheus)[1] == amount * boostTokenRate - math.floor(amount * boostTokenRate / 2)
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_5 + instant_value_5) * (blockTimestamp_5 - boosting_controller_mocked.boosts(morpheus)[
        3]) / 2) + math.floor((instant_value_5 + instant_value_4) * (boosting_controller_mocked.boosts(morpheus)[3] - blockTimestamp_4) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    # wait for some time (end of reduction + 2 * week)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime + 2 * week)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_6 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == amount
    assert boosting_controller_mocked.coinBalances(
        boosting_token_mocked) == amount
    assert blockTimestamp_6 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_6 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_6 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_6 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount * boostTokenRate
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + warmupTime + minLockTime
    assert boosting_controller_mocked.boosts(
        morpheus)[1] == amount * boostTokenRate - math.floor(amount * boostTokenRate / 2)
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_6 + instant_value_6) * (
        blockTimestamp_6 - blockTimestamp_5) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    # wait for some time (end of reduction + 3 * week)
    chain.mine(1, blockTimestamp +
               warmupTime + minLockTime + 3 * week)
    # unboost all tokens
    assert boosting_controller_mocked.availableToUnboost(
        boosting_token_mocked, morpheus) == amount
    tx4 = boosting_controller_mocked.unboost(
        boosting_token_mocked, {'from': morpheus})
    blockTimestamp_7 = chain.time()
    # check tx4 events
    assert tx4.return_value is None
    assert len(tx4.events) == 2
    assert tx4.events["Unboost"].values(
    ) == [boosting_token_mocked, morpheus, amount]
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == 0
    assert boosting_controller_mocked.coinBalances(boosting_token_mocked) == 0
    assert blockTimestamp_7 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_7 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_7 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == 0
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(morpheus)[2] == 0
    assert boosting_controller_mocked.boosts(morpheus)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_6 + instant_value_6) * (
        blockTimestamp_7 - blockTimestamp_6) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    previous_integral = boosting_controller_mocked.boostIntegral()
    # wait for some time
    chain.mine(1, chain.time() + week)
    blockTimestamp_8 = chain.time()
    assert boosting_controller_mocked.balances(
        boosting_token_mocked, morpheus) == 0
    assert boosting_controller_mocked.coinBalances(boosting_token_mocked) == 0
    assert blockTimestamp_8 >= boosting_controller_mocked.lastBoostTimestamp() + \
        week
    assert blockTimestamp_8 >= boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) + week
    assert boosting_controller_mocked.boostIntegral() == amount * boostTokenRate * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == 0
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(morpheus)[2] == 0
    assert boosting_controller_mocked.boosts(morpheus)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(
        morpheus) == previous_integral_morpheus
    assert boosting_controller_mocked.boostIntegral() == previous_integral
