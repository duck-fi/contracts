def test_mint_not_allowed(controller, reaper_1_mock, deployer, morpheus, exception_tester):
    exception_tester("reaper is not supported", controller.mintFor,
                     reaper_1_mock, deployer, {'from': deployer})
    controller.addReaper(reaper_1_mock, {'from': deployer})
    exception_tester("mint is not allowed", controller.mintFor,
                     reaper_1_mock, morpheus, {'from': deployer})


def test_mint_approval(controller, reaper_1_mock, deployer, morpheus):
    assert not controller.mintAllowance(reaper_1_mock, morpheus, deployer)
    controller.mintApprove(reaper_1_mock, deployer, True, {'from': morpheus})
    assert controller.mintAllowance(reaper_1_mock, morpheus, deployer)
    controller.mintApprove(reaper_1_mock, deployer, False, {'from': morpheus})
    assert not controller.mintAllowance(reaper_1_mock, morpheus, deployer)
