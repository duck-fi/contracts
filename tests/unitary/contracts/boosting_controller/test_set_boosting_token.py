def test_not_owner(boosting_controller_mocked, ownable_exception_tester, ZERO_ADDRESS, thomas):
    ownable_exception_tester(
        boosting_controller_mocked.setBoostingToken, ZERO_ADDRESS, {'from': thomas})


def test_set_zero_address(boosting_controller_mocked, exception_tester, ZERO_ADDRESS, deployer):
    exception_tester("zero address", boosting_controller_mocked.setBoostingToken,
                     ZERO_ADDRESS, {'from': deployer})


def test_set_once(exception_tester, boosting_controller_mocked, deployer, boosting_token_mocked, thomas):
    assert boosting_controller_mocked.boostingToken() == boosting_token_mocked
    exception_tester("set only once", boosting_controller_mocked.setBoostingToken,
                     thomas, {'from': deployer})
