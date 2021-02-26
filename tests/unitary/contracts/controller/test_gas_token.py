from brownie.test import given, strategy


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_vote_gas_reducing_not_valid_token(controller, reaper_mock, farm_token, exception_tester, deployer, amount, week):
    controller.addReaper(reaper_mock, {'from': deployer})
    exception_tester("unsupported gas token", controller.mintFor, reaper_mock, deployer, farm_token, {'from': deployer})


@given(amount=strategy('uint256', min_value=10 ** 10, max_value=10 ** 13))
def test_boost_farm_token(controller, reaper_mock, lp_token, farm_token, chi_token, deployer, morpheus, amount, week, chain):
    chi_token.mint(10, {'from': deployer})
    chi_token.transfer(morpheus, 10)
    chi_token.approve(controller, 10, {'from': morpheus})
    
    farm_token.setMinter(controller, {'from': deployer})
    farm_token.startEmission({'from': deployer})

    lp_token.transfer(morpheus, 100, {'from': deployer})
    lp_token.approve(reaper_mock, 100, {'from': morpheus})

    chain.mine(1, chain.time() + 1)
    reaper_mock.deposit(100, {'from': morpheus})
    initial_balance_morpheus = chi_token.balanceOf(morpheus)

    controller.mintFor(reaper_mock, morpheus, chi_token, {'from': morpheus})
    assert initial_balance_morpheus - chi_token.balanceOf(morpheus) == 1
    initial_balance_morpheus = chi_token.balanceOf(morpheus)

    chain.mine(1, chain.time() + week + 1)
    controller.mintFor(reaper_mock, morpheus, chi_token, {'from': morpheus})
    assert initial_balance_morpheus - chi_token.balanceOf(morpheus) == 3
    initial_balance_morpheus = chi_token.balanceOf(morpheus)

    chain.mine(1, chain.time() + week + 1)
    controller.mintFor(reaper_mock, morpheus, chi_token, {'from': morpheus})
    assert initial_balance_morpheus - chi_token.balanceOf(morpheus) == 2
