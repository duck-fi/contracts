def test_reaper_admin_fee(farm_contracts, deployer, morpheus, trinity, chain, day, week, exception_tester):
    controller = farm_contracts['controller']
    voting_controller = farm_contracts['voting_controller']
    ducks = farm_contracts['ducks']

    controller.startEmission(0, {'from': deployer})

    usdn_usdt_lp = farm_contracts['usdn_usdt_lp']
    reaper = farm_contracts['usdn_usdt_reaper']
    uniswap_strategy_v1 = farm_contracts['uniswap_strategy_v1']
    usdn_mpool_gauge = farm_contracts['usdn_mpool_gauge']

    usdn_usdt_lp.approve(reaper, 1000, {'from': deployer})
    tx1 = reaper.deposit(1000, {'from': deployer})

    assert reaper.balances(deployer) == 1000
    assert usdn_usdt_lp.balanceOf(reaper) == 1000
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    chain.mine(1, tx1.timestamp + 2 * week)

    usdn_usdt_lp.transfer(morpheus, 1000, {'from': deployer})
    usdn_usdt_lp.approve(reaper, 1000, {'from': morpheus})
    tx2 = reaper.deposit(1000, morpheus, True, {'from': morpheus})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.totalBalances() == 2000
    assert usdn_usdt_lp.balanceOf(reaper) == 2000
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    exception_tester("not supported", reaper.invest, {'from': deployer})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.totalBalances() == 2000
    assert usdn_usdt_lp.balanceOf(reaper) == 2000
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0
    assert reaper.adminFee() == 15

    chain.mine(1, tx1.timestamp + 2 * week)
    reaper.setAdminFee(500, {'from': deployer}) # 50%

    chain.mine(1, tx2.timestamp + 2 * week)

    usdn_usdt_lp.transfer(trinity, 1000, {'from': deployer})
    usdn_usdt_lp.approve(reaper, 1000, {'from': trinity})
    tx4 = reaper.deposit(1000, trinity, True, {'from': trinity})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.balances(trinity) == 1000
    assert reaper.totalBalances() == 3000
    assert usdn_usdt_lp.balanceOf(reaper) == 3000
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    reaper.snapshot({'from': morpheus})
    assert reaper.adminFee() == 500
    assert reaper.reapIntegralFor(morpheus) > 0
    assert reaper.reapIntegralFor(reaper) > 0
    assert abs(reaper.reapIntegralFor(reaper) - reaper.reapIntegralFor(morpheus) // 2) <= 10
    last_reapIntegralFor_reaper = reaper.reapIntegralFor(reaper)
    last_reapIntegralFor_morpheus = reaper.reapIntegralFor(morpheus)

    # claim admin fee
    ducks_balance = ducks.balanceOf(deployer)
    controller.claimAdminFee(reaper, {'from': deployer})
    assert ducks.balanceOf(deployer) == ducks_balance + reaper.reapIntegralFor(reaper)

    reaper.setAdminFee(1000, {'from': deployer}) # 100%
    reaper.snapshot({'from': morpheus})
    assert reaper.reapIntegralFor(morpheus) > 0
    assert reaper.reapIntegralFor(reaper) > 0
    assert abs((reaper.reapIntegralFor(reaper) - last_reapIntegralFor_reaper) - (reaper.reapIntegralFor(morpheus) - last_reapIntegralFor_morpheus)) <= 10

    # claim admin fee
    ducks_balance = ducks.balanceOf(deployer)
    controller.claimAdminFee(reaper, {'from': deployer})
    assert ducks.balanceOf(deployer) == ducks_balance + reaper.reapIntegralFor(reaper) - last_reapIntegralFor_reaper

    # withdraw is not activated yet
    exception_tester("withdraw is locked", reaper.withdraw, 500, {'from': morpheus})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 1000
    assert reaper.balances(trinity) == 1000
    assert reaper.totalBalances() == 3000
    assert usdn_usdt_lp.balanceOf(reaper) == 3000
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    # claim ducks is not activated yet
    exception_tester("minting is not started yet", controller.mintFor, reaper, {'from': morpheus})

    # activate withdraw on strategy
    uniswap_strategy_v1.activate({'from': deployer})

    # withdraw
    tx5 = reaper.withdraw(500, {'from': morpheus})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 500
    assert reaper.balances(trinity) == 1000
    assert reaper.totalBalances() == 2500
    assert usdn_usdt_lp.balanceOf(reaper) == 2500
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    tx6 = reaper.withdraw(1000, {'from': trinity})

    assert reaper.balances(deployer) == 1000
    assert reaper.balances(morpheus) == 500
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 1500
    assert usdn_usdt_lp.balanceOf(reaper) == 1500
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    tx7 = reaper.withdraw(1000, {'from': deployer})
    
    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 500
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 500
    assert usdn_usdt_lp.balanceOf(reaper) == 500
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    tx7 = reaper.withdraw(500, {'from': morpheus})

    assert reaper.balances(deployer) == 0
    assert reaper.balances(morpheus) == 0
    assert reaper.balances(trinity) == 0
    assert reaper.totalBalances() == 0
    assert usdn_usdt_lp.balanceOf(reaper) == 0
    assert usdn_usdt_lp.balanceOf(uniswap_strategy_v1) == 0

    # now claim ducks reward
    controller.startMinting({'from': deployer})

    ducks_balance_deployer = ducks.balanceOf(deployer)
    controller.mintFor(reaper, {'from': deployer})
    assert ducks.balanceOf(deployer) == ducks_balance_deployer + reaper.reapIntegralFor(deployer)
    ducks_balance_deployer = ducks.balanceOf(deployer)
    controller.mintFor(reaper, {'from': deployer})
    assert ducks.balanceOf(deployer) == ducks_balance_deployer

    ducks_balance_morpheus = ducks.balanceOf(morpheus)
    controller.mintFor(reaper, {'from': morpheus})
    assert ducks.balanceOf(morpheus) == ducks_balance_morpheus + reaper.reapIntegralFor(morpheus)
    ducks_balance_morpheus = ducks.balanceOf(morpheus)
    controller.mintFor(reaper, {'from': morpheus})
    assert ducks.balanceOf(morpheus) == ducks_balance_morpheus

    ducks_balance_trinity = ducks.balanceOf(trinity)
    controller.mintFor(reaper, {'from': trinity})
    assert ducks.balanceOf(trinity) == ducks_balance_trinity + reaper.reapIntegralFor(trinity)
    ducks_balance_trinity = ducks.balanceOf(trinity)
    controller.mintFor(reaper, {'from': trinity})
    assert ducks.balanceOf(trinity) == ducks_balance_trinity
