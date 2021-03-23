import math


def test_deposit_escrow_zero_amount(curve_staker_mocked, exception_tester, deployer):
    exception_tester("nothing to deposit", curve_staker_mocked.depositToEscrow, 0, {'from': deployer})


def test_withdraw_escrow_zero_amount(curve_staker_mocked, exception_tester, deployer):
    exception_tester("nothing to withdraw", curve_staker_mocked.withdrawFromEscrow, {'from': deployer})


def test_set_locking_period_owner_only(curve_staker_mocked, ownable_exception_tester, morpheus):
    ownable_exception_tester(curve_staker_mocked.setLockingPeriod, 1, {'from': morpheus})


def test_set_locking_period_wrong_value(curve_staker_mocked, exception_tester, deployer, day, year):
    exception_tester("month <= locking period <= 4 year", curve_staker_mocked.setLockingPeriod, 30 * day - 1, {'from': deployer})
    exception_tester("month <= locking period <= 4 year", curve_staker_mocked.setLockingPeriod, 4 * year + 1, {'from': deployer})


def test_set_locking_period(curve_staker_mocked, day, year, deployer):
    assert curve_staker_mocked.lockingPeriod() == year
    curve_staker_mocked.setLockingPeriod(30 * day, {'from': deployer})
    assert curve_staker_mocked.lockingPeriod() == 30 * day


def test_escrow(curve_staker_mocked, curve_gauge_mock, curve_minter_mock, crv_token_mock, curve_ve_mock, exception_tester, deployer, morpheus, trinity, chain, day, week):
    # deployer <=> reaper strategy
    curve_staker_mocked.setReaperStrategy(deployer, {'from': deployer})
    
    # give approve for curve_staker_mocked from deployer
    crv_token_mock.transfer(morpheus, 5000, {'from': deployer})
    crv_token_mock.transfer(trinity, 5000, {'from': deployer})
    crv_token_mock.approve(curve_staker_mocked, 5000, {'from': deployer})
    crv_token_mock.approve(curve_staker_mocked, 5000, {'from': morpheus})
    crv_token_mock.approve(curve_staker_mocked, 5000, {'from': trinity})
    initial_balance = crv_token_mock.balanceOf(deployer)

    # give approve for VE contract from curve_staker_mocked
    crv_token_mock.approve(curve_ve_mock, 2 ** 256 - 1, {'from': curve_staker_mocked})

    tx1 = curve_staker_mocked.depositToEscrow(1000, {'from': deployer})
    assert crv_token_mock.balanceOf(deployer) == initial_balance - 1000
    unlock_timestamp = math.floor((tx1.timestamp + curve_staker_mocked.lockingPeriod()) * week / week)
    
    chain.mine(1, unlock_timestamp - 10)

    exception_tester("withdraw is locked", curve_staker_mocked.withdrawFromEscrow, {'from': deployer})

    chain.mine(1, unlock_timestamp + 1)

    # new deposit is needed, can't withdraw
    exception_tester("", curve_staker_mocked.withdrawFromEscrow, {'from': deployer})

    exception_tester("withdrawal unlocked amount or renewal is needed", curve_staker_mocked.depositToEscrow, 1100, False, {'from': deployer}) 
    exception_tester("withdrawal unlocked amount or renewal is needed", curve_staker_mocked.depositToEscrow, 1000, False, {'from': deployer}) 
    exception_tester("withdrawal extra unlocked amount is needed", curve_staker_mocked.depositToEscrow, 900, True, {'from': deployer})

    tx2 = curve_staker_mocked.depositToEscrow(2000, True, {'from': deployer})
    assert crv_token_mock.balanceOf(deployer) == initial_balance - 2000
    unlock_timestamp = math.floor((tx2.timestamp + curve_staker_mocked.lockingPeriod()) * week / week)

    chain.mine(1, tx2.timestamp + 1000)

    exception_tester("no unlocked amount for renewal", curve_staker_mocked.depositToEscrow, 1000, True, {'from': morpheus})
    tx3 = curve_staker_mocked.depositToEscrow(1000, False, {'from': morpheus})
    assert crv_token_mock.balanceOf(morpheus) == 5000 - 1000

    exception_tester("withdraw is locked", curve_staker_mocked.withdrawFromEscrow, {'from': deployer})
    exception_tester("withdraw is locked", curve_staker_mocked.withdrawFromEscrow, {'from': morpheus})

    chain.mine(1, unlock_timestamp + 1)

    # new deposit is needed, can't withdraw
    exception_tester("", curve_staker_mocked.withdrawFromEscrow, {'from': deployer})
    exception_tester("", curve_staker_mocked.withdrawFromEscrow, {'from': morpheus})
    exception_tester("nothing to withdraw", curve_staker_mocked.withdrawFromEscrow, {'from': trinity})

    exception_tester("no unlocked amount for renewal", curve_staker_mocked.depositToEscrow, 1, True, {'from': trinity})
    tx4 = curve_staker_mocked.depositToEscrow(1, False, {'from': trinity})
    assert crv_token_mock.balanceOf(trinity) == 5000 - 1
    unlock_timestamp = math.floor((tx4.timestamp + curve_staker_mocked.lockingPeriod()) * week / week)

    chain.mine(1, tx4.timestamp + 500)

    curve_staker_mocked.withdrawFromEscrow({'from': deployer})
    assert crv_token_mock.balanceOf(deployer) == initial_balance

    curve_staker_mocked.withdrawFromEscrow({'from': morpheus})
    assert crv_token_mock.balanceOf(morpheus) == 5000
