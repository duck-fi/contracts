def test_init(voting_controller_mocked, controller_mock, gas_token_check_list, farm_token):
    assert voting_controller_mocked.controller() == controller_mock
    assert voting_controller_mocked.gasTokenCheckList() == gas_token_check_list
    assert voting_controller_mocked.farmToken() == farm_token
