def test_not_owner(controller, ownable_exception_tester, ZERO_ADDRESS, thomas):
    ownable_exception_tester(
        controller.setAdmin, ZERO_ADDRESS, {'from': thomas})


def test_set_zero_address(controller, exception_tester, ZERO_ADDRESS, deployer):
    exception_tester("zero address", controller.setAdmin,
                     ZERO_ADDRESS, {'from': deployer})


def test_success(controller, deployer, thomas):
    assert controller.admin() == deployer
    controller.setAdmin(thomas, {'from': deployer})
    assert controller.admin() == thomas
