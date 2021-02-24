def test_init(initial_emission_distributor, gas_token_check_list, farm_token):
    assert initial_emission_distributor.gasTokenCheckList() == gas_token_check_list
    assert initial_emission_distributor.farmToken() == farm_token
