import math
from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_update_on_lock(exception_tester, boosting_controller_mocked, boosting_token_mocked, deployer, amount, delta, chain, week, day):
    warmupTime = 2 * week

    # boost 1st time
    boosting_token_mocked.mint(deployer, 100 * amount, {'from': deployer})
    boosting_token_mocked.approve(boosting_controller_mocked,
                                  amount, {'from': deployer})
    boosting_controller_mocked.boost(amount, 4 * week, {'from': deployer})
    blockTimestamp = chain.time()

    assert boosting_controller_mocked.balances(deployer) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert boosting_controller_mocked.boostIntegral() == 0
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boostIntegralFor(deployer) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        deployer) == blockTimestamp

    # wait for some time (warmup + 1/4 of lock + delta)
    chain.mine(
        1, blockTimestamp + warmupTime + (4 * week - warmupTime) / 4 + delta)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(deployer)
    blockTimestamp_1 = chain.time()

    assert boosting_controller_mocked.balances(deployer) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == amount
    assert boosting_controller_mocked.boosts(
        deployer)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        deployer)[3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boosts(deployer)[1] == amount
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor((boosting_controller_mocked.boosts(deployer)[1] + amount) * (
        blockTimestamp_1 - boosting_controller_mocked.boosts(deployer)[2]) / 2) + math.floor(amount * warmupTime / 2)) <= 1

    exception_tester("tokens are locked",
                     boosting_controller_mocked.unboost, {'from': deployer})

    # wait for some time (warmup + lock + 1)
    chain.mine(1, blockTimestamp + 4 * week + 1)

    # unboost all tokens
    boosting_controller_mocked.unboost({'from': deployer})
    blockTimestamp_2 = chain.time()

    assert boosting_controller_mocked.balances(deployer) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        deployer)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() - blockTimestamp)
    assert boosting_controller_mocked.boosts(deployer)[0] == 0
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(deployer)[2] == 0
    assert boosting_controller_mocked.boosts(deployer)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(deployer) - (math.floor(amount * (blockTimestamp_2 - (
        blockTimestamp + warmupTime))) + math.floor(amount * warmupTime / 2)) <= 1
    previous_integral_deployer = boosting_controller_mocked.boostIntegralFor(
        deployer)
    previous_integral = boosting_controller_mocked.boostIntegral()

    # wait for some time
    chain.mine(1, chain.time() + day)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(deployer)
    blockTimestamp_3 = chain.time()

    assert boosting_controller_mocked.balances(deployer) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_3 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - \
        boosting_controller_mocked.lastBoostTimestampFor(deployer) <= 1
    assert boosting_controller_mocked.boosts(deployer)[0] == 0
    assert boosting_controller_mocked.boosts(deployer)[1] == 0
    assert boosting_controller_mocked.boosts(deployer)[2] == 0
    assert boosting_controller_mocked.boosts(deployer)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(
        deployer) == previous_integral_deployer
    assert boosting_controller_mocked.boostIntegral() == previous_integral


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_update_after_reduction(boosting_controller_mocked, boosting_token_mocked, deployer, morpheus, amount, delta, week, day, chain):
    warmupTime = 2 * week

    initial_boost_integral = boosting_controller_mocked.boostIntegral()

    # boost 1st time
    boosting_token_mocked.mint(morpheus, 100 * amount, {'from': deployer})
    boosting_token_mocked.approve(boosting_controller_mocked,
                                  amount, {'from': morpheus})
    boosting_controller_mocked.boost(amount, 4 * week, {'from': morpheus})
    blockTimestamp = chain.time()

    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert boosting_controller_mocked.boostIntegral() == initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(morpheus)[
        3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boostIntegralFor(morpheus) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        morpheus) == blockTimestamp

    # wait for some time (warmup + lock + delta)
    chain.mine(
        1, blockTimestamp + 4 * week + delta)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(morpheus)
    blockTimestamp_1 = chain.time()

    assert boosting_controller_mocked.balances(morpheus) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == amount
    assert boosting_controller_mocked.boosts(
        morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(
        morpheus)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(morpheus)[
        3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor(0 * (blockTimestamp_1 - boosting_controller_mocked.boosts(morpheus)[3])) + math.floor(
        amount * (boosting_controller_mocked.boosts(morpheus)[3] - boosting_controller_mocked.boosts(morpheus)[2])) + math.floor(amount * warmupTime / 2)) <= 1

    # unboost all tokens
    boosting_controller_mocked.unboost({'from': morpheus})
    blockTimestamp_2 = chain.time()

    assert boosting_controller_mocked.balances(morpheus) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        morpheus)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(morpheus)[0] == 0
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(morpheus)[2] == 0
    assert boosting_controller_mocked.boosts(morpheus)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(morpheus) - (math.floor(
        amount * (4 * week - warmupTime)) + math.floor(amount * warmupTime / 2)) <= 1
    previous_integral_morpheus = boosting_controller_mocked.boostIntegralFor(
        morpheus)
    previous_integral = boosting_controller_mocked.boostIntegral()

    # wait for some time
    chain.mine(1, chain.time() + day)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(morpheus)
    blockTimestamp_3 = chain.time()

    assert boosting_controller_mocked.balances(morpheus) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_3 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - \
        boosting_controller_mocked.lastBoostTimestampFor(morpheus) <= 1
    assert boosting_controller_mocked.boosts(morpheus)[0] == 0
    assert boosting_controller_mocked.boosts(morpheus)[1] == 0
    assert boosting_controller_mocked.boosts(morpheus)[2] == 0
    assert boosting_controller_mocked.boosts(morpheus)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(
        morpheus) == previous_integral_morpheus
    assert boosting_controller_mocked.boostIntegral() == previous_integral


@given(amount=strategy('uint256', min_value=10**10, max_value=10**13), delta=strategy('uint256', min_value=8640, max_value=86400*3))
def test_boost_update_on_warmup_and_after_lock(boosting_controller_mocked, boosting_token_mocked, deployer, trinity, amount, delta, week, day, chain):
    warmupTime = 2 * week
    initial_boost_integral = boosting_controller_mocked.boostIntegral()

    # boost 1st time
    boosting_token_mocked.mint(trinity, 100 * amount, {'from': deployer})
    boosting_token_mocked.approve(boosting_controller_mocked,
                                  amount, {'from': trinity})
    boosting_controller_mocked.boost(amount, 4 * week, {'from': trinity})
    blockTimestamp = chain.time()

    assert boosting_controller_mocked.balances(trinity) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert boosting_controller_mocked.boostIntegral() == initial_boost_integral
    assert blockTimestamp - boosting_controller_mocked.lastBoostTimestamp() <= 1
    blockTimestamp = boosting_controller_mocked.lastBoostTimestamp()
    assert boosting_controller_mocked.boosts(trinity)[0] == amount
    assert boosting_controller_mocked.boosts(trinity)[1] == 0
    assert boosting_controller_mocked.boosts(
        trinity)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        trinity)[3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boostIntegralFor(trinity) == 0
    assert boosting_controller_mocked.lastBoostTimestampFor(
        trinity) == blockTimestamp

    # wait for some time (up to half of warmup + delta)
    chain.mine(1, blockTimestamp +
               warmupTime / 2 + delta)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(trinity)
    blockTimestamp_1 = chain.time()

    assert boosting_controller_mocked.balances(trinity) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_1 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_1 - \
        boosting_controller_mocked.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_1 = boosting_controller_mocked.lastBoostTimestampFor(
        trinity)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(trinity)[0] == amount
    assert boosting_controller_mocked.boosts(trinity)[
        1] == amount * (blockTimestamp_1 - blockTimestamp) / warmupTime
    assert boosting_controller_mocked.boosts(
        trinity)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        trinity)[3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boostIntegralFor(trinity) == math.floor(
        boosting_controller_mocked.boosts(trinity)[1] * (blockTimestamp_1 - blockTimestamp) / 2)

    # wait for some time (warmup + reduction + delta)
    chain.mine(
        1, blockTimestamp + 4 * week + delta)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(trinity)
    blockTimestamp_2 = chain.time()

    assert boosting_controller_mocked.balances(trinity) == amount
    assert boosting_controller_mocked.totalBalance() == amount
    assert blockTimestamp_2 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_2 - \
        boosting_controller_mocked.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_2 = boosting_controller_mocked.lastBoostTimestampFor(
        trinity)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(trinity)[0] == amount
    assert boosting_controller_mocked.boosts(
        trinity)[1] == 0
    assert boosting_controller_mocked.boosts(
        trinity)[2] == blockTimestamp + warmupTime
    assert boosting_controller_mocked.boosts(
        trinity)[3] == blockTimestamp + 4 * week
    assert boosting_controller_mocked.boostIntegralFor(trinity) - (math.floor(amount * (boosting_controller_mocked.boosts(
        trinity)[3] - boosting_controller_mocked.boosts(trinity)[2])) + math.floor(amount * warmupTime / 2)) <= 1

    # unboost all tokens
    boosting_controller_mocked.unboost({'from': trinity})
    blockTimestamp_3 = chain.time()

    assert boosting_controller_mocked.balances(trinity) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_3 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_3 - \
        boosting_controller_mocked.lastBoostTimestampFor(trinity) <= 1
    blockTimestamp_3 = boosting_controller_mocked.lastBoostTimestampFor(
        trinity)
    assert boosting_controller_mocked.boostIntegral() == amount * \
        (boosting_controller_mocked.lastBoostTimestamp() -
         blockTimestamp) + initial_boost_integral
    assert boosting_controller_mocked.boosts(trinity)[0] == 0
    assert boosting_controller_mocked.boosts(trinity)[1] == 0
    assert boosting_controller_mocked.boosts(trinity)[2] == 0
    assert boosting_controller_mocked.boosts(trinity)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(trinity) - (math.floor(
        amount * (4 * week - warmupTime)) + math.floor(amount * warmupTime / 2)) <= 1
    previous_integral_trinity = boosting_controller_mocked.boostIntegralFor(
        trinity)
    previous_integral = boosting_controller_mocked.boostIntegral()

    # wait for some time
    chain.mine(1, chain.time() + day)

    boosting_controller_mocked.updateAccountBoostFactorIntegral(trinity)
    blockTimestamp_4 = chain.time()

    assert boosting_controller_mocked.balances(trinity) == 0
    assert boosting_controller_mocked.totalBalance() == 0
    assert blockTimestamp_4 - boosting_controller_mocked.lastBoostTimestamp() <= 1
    assert blockTimestamp_4 - \
        boosting_controller_mocked.lastBoostTimestampFor(trinity) <= 1
    assert boosting_controller_mocked.boosts(trinity)[0] == 0
    assert boosting_controller_mocked.boosts(trinity)[1] == 0
    assert boosting_controller_mocked.boosts(trinity)[2] == 0
    assert boosting_controller_mocked.boosts(trinity)[3] == 0
    assert boosting_controller_mocked.boostIntegralFor(
        trinity) == previous_integral_trinity
    assert boosting_controller_mocked.boostIntegral() == previous_integral
