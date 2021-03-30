import math
from brownie.test import given, strategy


def test_boost_short_locktime(boosting_controller_mocked, boosting_token_mocked, deployer, exception_tester):
    boosting_token_mocked.mint(deployer, 10**26, {'from': deployer})
    assert boosting_controller_mocked.availableToUnboost(deployer) == 0
    exception_tester("locktime is too short",
                     boosting_controller_mocked.boost, 1, 1, {'from': deployer})


def test_boost_not_approved(boosting_controller_mocked, farm_token, deployer, morpheus, exception_tester, week):
    assert boosting_controller_mocked.availableToUnboost(deployer) == 0
    exception_tester("", boosting_controller_mocked.boost,
                     1, 2 * week, {'from': morpheus})


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost(boosting_controller_mocked, boosting_token_mocked, deployer, morpheus, amount, delta, chain, week):
    lockTime = 4 * week
    warmupTime = 2 * week
    initial_boost_integral = boosting_controller_mocked.boostIntegral()

    # boost with boosting_token 1st time
    boosting_token_mocked.mint(morpheus, 5 * amount, {'from': deployer})
    boosting_token_mocked.approve(
        boosting_controller_mocked, 5 * amount, {'from': morpheus})
    tx1 = boosting_controller_mocked.boost(
        amount, lockTime, {'from': morpheus})
    blockTimestamp = chain.time()

    # check tx1 event
    assert tx1.return_value is None
    assert len(tx1.events) == 2
    assert tx1.events["Boost"].values() == [morpheus, amount, lockTime]
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert boosting_controller_mocked.boostIntegral() == 0 + initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) == blockTimestamp

    # wait for some time (quater of warmup - delta)
    chain.mine(1, blockTimestamp +
               warmupTime / 4 - delta)
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert boosting_controller_mocked.boostIntegral() == 0 + initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() == 0
    assert boosting_controller_mocked.boosts(morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) == blockTimestamp

    # wait for some time (up to quater of warmup)
    chain.mine(1, blockTimestamp + warmupTime / 4)
    tx2 = boosting_controller_mocked.updateBoostIntegral()
    tx3 = boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_1 = chain.time()
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_1 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(morpheus)[
        1] == amount * (blockTimestamp_1 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
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
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_2 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(morpheus)[
        1] == amount * (blockTimestamp_2 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == math.floor((instant_value_2 + instant_value_1) * (
        blockTimestamp_2 - blockTimestamp_1) / 2) + math.floor((instant_value_1 + 0) * (blockTimestamp_1 - blockTimestamp) / 2)
    assert tx2.return_value == boosting_controller_mocked.boostIntegral()
    assert tx3.return_value == boosting_controller_mocked.boostIntegralFor(
        morpheus)
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)

    # wait for some time (end of warmup + quater of reduction)
    chain.mine(1, blockTimestamp +
               warmupTime + (lockTime - warmupTime) / 4)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_3 = chain.time()
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_3 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_3 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_3 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boosts(morpheus)[1] == amount
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_3 + amount) * (blockTimestamp_3 - boosting_controller_mocked.boosts(morpheus)[
        2]) / 2) + math.floor((amount + instant_value_2) * (boosting_controller_mocked.boosts(morpheus)[2] - blockTimestamp_2) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)

    # wait for some time (end of warmup + 3/4 of reduction)
    chain.mine(1, blockTimestamp +
               warmupTime + (lockTime - warmupTime) * 3 / 4)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_4 = chain.time()
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_4 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_4 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_4 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boosts(morpheus)[1] == amount
    assert instant_value_3 == instant_value_4
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_4 + instant_value_3) * (
        blockTimestamp_4 - blockTimestamp_3) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)

    # wait for some time (end of reduction + week)
    chain.mine(1, blockTimestamp + lockTime + week)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_5 = chain.time()
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_5 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_5 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_5 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_5 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boosts(
        morpheus)[1] == 0
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor(instant_value_5 * (blockTimestamp_5 - boosting_controller_mocked.boosts(morpheus)[
        3])) + math.floor(instant_value_4 * (boosting_controller_mocked.boosts(morpheus)[3] - blockTimestamp_4)) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)

    # wait for some time (end of reduction + 2 * week)
    chain.mine(1, blockTimestamp + lockTime + 2 * week)
    boosting_controller_mocked.updateBoostIntegral()
    boosting_controller_mocked.accountBoostIntegral(morpheus)
    blockTimestamp_6 = chain.time()
    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_6 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_6 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_6 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    instant_value_6 = boosting_controller_mocked.boosts(morpheus)[1]
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(
        morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        morpheus)[3] == blockTimestamp + lockTime
    assert boosting_controller_mocked.boosts(
        morpheus)[1] == 0
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor((instant_value_6 + instant_value_6) * (
        blockTimestamp_6 - blockTimestamp_5) / 2) + previous_integral_morpheus) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)

    # wait for some time (end of reduction + 3 * week)
    chain.mine(1, blockTimestamp + lockTime + 3 * week)

    # unboost all tokens
    assert boosting_controller_mocked.availableToUnboost(morpheus) == amount
    tx4 = boosting_controller_mocked.unboost({'from': morpheus})
    blockTimestamp_7 = chain.time()

    # check tx4 events
    assert tx4.return_value is None
    assert len(tx4.events) == 2
    assert tx4.events["Unboost"].values(
    ) == [morpheus, amount]
    assert boosting_controller_mocked.balances(morpheus) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_7 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_7 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_7 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    assert boosting_controller_mocked.boostIntegral() == amount * \
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
    assert boosting_controller_mocked.balances(morpheus) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_8 >= boosting_controller_mocked.lastBoostTimestamp() + \
        week
    assert blockTimestamp_8 >= boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) + week
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == 0
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(morpheus)[2] == 0
    assert boosting_controller_mocked.boosts(morpheus)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(
        morpheus) == previous_integral_morpheus
    assert boosting_controller_mocked.boostIntegral() == previous_integral
