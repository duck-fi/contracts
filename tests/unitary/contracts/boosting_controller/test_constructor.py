def test_init(boosting_controller_mocked, gas_token_check_list, contract_white_list):
    assert boosting_controller_mocked.gasTokenCheckList() == gas_token_check_list
    assert boosting_controller_mocked.contractCheckList() == contract_white_list
