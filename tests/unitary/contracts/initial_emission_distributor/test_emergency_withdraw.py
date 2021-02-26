def test_not_owner(initial_emission_distributor, ownable_exception_tester, thomas):
    ownable_exception_tester(
        initial_emission_distributor.emergencyWithdraw, {'from': thomas})


def test_set_once(initial_emission_distributor, deployer, farm_token):
    initial_balance = farm_token.balanceOf(deployer)
    assert farm_token.balanceOf(initial_emission_distributor) == 0
    farm_token.transfer(initial_emission_distributor,
                        1_000, {'from': deployer})
    assert farm_token.balanceOf(initial_emission_distributor) == 1_000
    initial_emission_distributor.emergencyWithdraw({'from': deployer})
    assert farm_token.balanceOf(deployer) == initial_balance
