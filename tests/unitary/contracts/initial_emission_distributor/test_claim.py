def fill_array(value, length):
    result = []
    for i in range(0, length):
        result.append(value)
    return result


def test_set_balance_not_owner(initial_emission_distributor, ownable_exception_tester, ZERO_ADDRESS, thomas):
    ownable_exception_tester(
        initial_emission_distributor.setBalances, fill_array(ZERO_ADDRESS, 100), fill_array(0, 100), ZERO_ADDRESS, {'from': thomas})


def test_start_claiming_not_owner(initial_emission_distributor, ownable_exception_tester, thomas):
    ownable_exception_tester(
        initial_emission_distributor.startClaiming, {'from': thomas})


def test_claim(exception_tester, initial_emission_distributor, farm_token, ZERO_ADDRESS, morpheus, trinity, deployer, chain, year, chi_token):
    farm_token.transfer(initial_emission_distributor,
                        10_000_000, {'from': deployer})
    addresses = fill_array(ZERO_ADDRESS, 100)
    amounts = fill_array(0, 100)
    addresses[0] = morpheus
    amounts[0] = 1_000_000
    addresses[1] = trinity
    amounts[1] = 2_000_000

    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 0

    initial_emission_distributor.setBalances(
        addresses, amounts, ZERO_ADDRESS, {'from': deployer})

    # claiming is not started
    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 0
    exception_tester("claiming is not started",
                     initial_emission_distributor.claim, {'from': deployer})
    exception_tester("claiming is not started",
                     initial_emission_distributor.claim, {'from': morpheus})
    exception_tester("claiming is not started",
                     initial_emission_distributor.claim, {'from': morpheus})

    initial_emission_distributor.startClaiming({'from': deployer})
    exception_tester("claiming already started",
                     initial_emission_distributor.setBalances, addresses, amounts, ZERO_ADDRESS, {'from': deployer})
    exception_tester("claiming already started",
                     initial_emission_distributor.startClaiming, {'from': deployer})
    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 0

    chain.mine(1, chain.time() + year / 2)
    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 500_000
    assert initial_emission_distributor.claimableTokens(trinity) == 1_000_000

    initial_emission_distributor.claim({'from': morpheus})
    assert farm_token.balanceOf(morpheus) == 500_000
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 1_000_000

    chain.mine(1, chain.time() + year / 2 + 1)
    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 500_000
    assert initial_emission_distributor.claimableTokens(trinity) == 2_000_000

    initial_emission_distributor.claim({'from': morpheus})
    assert farm_token.balanceOf(morpheus) == 1_000_000
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 2_000_000
    initial_emission_distributor.claim({'from': trinity})
    assert farm_token.balanceOf(trinity) == 2_000_000
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 0

    chain.mine(1, chain.time() + year)
    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 0

    chi_token.mint(10, {'from': trinity})
    chi_token.approve(initial_emission_distributor, 10, {'from': trinity})
    initial_emission_distributor.claim(trinity, chi_token, {'from': trinity})
    assert 10 - chi_token.balanceOf(trinity) == 1
    assert initial_emission_distributor.claimableTokens(deployer) == 0
    assert initial_emission_distributor.claimableTokens(morpheus) == 0
    assert initial_emission_distributor.claimableTokens(trinity) == 0


def test_vote_gas_reducing_not_valid_token(initial_emission_distributor, exception_tester, trinity, farm_token):
    exception_tester("unsupported gas token", initial_emission_distributor.claim,
                     trinity, farm_token, {'from': trinity})
