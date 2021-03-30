def test_init(boosting_controller_mocked, gas_token_check_list):
    assert boosting_controller_mocked.gasTokenCheckList() == gas_token_check_list
