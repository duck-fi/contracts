def test_init(controller, gas_token_check_list, deployer):
    assert controller.gasTokenCheckList() == gas_token_check_list
    assert controller.admin() == deployer
