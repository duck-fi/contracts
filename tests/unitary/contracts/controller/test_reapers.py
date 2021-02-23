def test_add_reaper_owner_only(controller, reaper_1_mock, reaper_2_mock, reaper_3_mock, morpheus, ownable_exception_tester):
    ownable_exception_tester(controller.addReaper, reaper_1_mock, {'from': morpheus})
    ownable_exception_tester(controller.addReaper, reaper_2_mock, {'from': morpheus})
    ownable_exception_tester(controller.addReaper, reaper_3_mock, {'from': morpheus})


def test_remove_reaper_owner_only(controller, reaper_1_mock, reaper_2_mock, reaper_3_mock, morpheus, ownable_exception_tester):
    ownable_exception_tester(controller.removeReaper, reaper_1_mock, {'from': morpheus})
    ownable_exception_tester(controller.removeReaper, reaper_2_mock, {'from': morpheus})
    ownable_exception_tester(controller.removeReaper, reaper_3_mock, {'from': morpheus})


def test_add_reapers(controller, reaper_1_mock, reaper_2_mock, reaper_3_mock, deployer, ZERO_ADDRESS, exception_tester):
    assert controller.lastReaperIndex() == 0
    assert controller.indexByReaper(reaper_1_mock) == 0
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 0
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == ZERO_ADDRESS
    assert controller.reapers(2) == ZERO_ADDRESS
    assert controller.reapers(3) == ZERO_ADDRESS
    
    controller.addReaper(reaper_1_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 1
    assert controller.indexByReaper(reaper_1_mock) == 1
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 0
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_1_mock
    assert controller.reapers(2) == ZERO_ADDRESS
    assert controller.reapers(3) == ZERO_ADDRESS

    exception_tester("reaper is exist", controller.addReaper, reaper_1_mock, {'from': deployer})

    controller.removeReaper(reaper_1_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 0
    assert controller.indexByReaper(reaper_1_mock) == 0
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 0
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_1_mock
    assert controller.reapers(2) == ZERO_ADDRESS
    assert controller.reapers(3) == ZERO_ADDRESS

    controller.addReaper(reaper_3_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 1
    assert controller.indexByReaper(reaper_1_mock) == 0
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 1
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_3_mock
    assert controller.reapers(2) == ZERO_ADDRESS
    assert controller.reapers(3) == ZERO_ADDRESS

    controller.addReaper(reaper_1_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 2
    assert controller.indexByReaper(reaper_1_mock) == 2
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 1
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_3_mock
    assert controller.reapers(2) == reaper_1_mock
    assert controller.reapers(3) == ZERO_ADDRESS

    controller.addReaper(reaper_2_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 3
    assert controller.indexByReaper(reaper_1_mock) == 2
    assert controller.indexByReaper(reaper_2_mock) == 3
    assert controller.indexByReaper(reaper_3_mock) == 1
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_3_mock
    assert controller.reapers(2) == reaper_1_mock
    assert controller.reapers(3) == reaper_2_mock
    
    controller.removeReaper(reaper_1_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 2
    assert controller.indexByReaper(reaper_1_mock) == 0
    assert controller.indexByReaper(reaper_2_mock) == 2
    assert controller.indexByReaper(reaper_3_mock) == 1
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_3_mock
    assert controller.reapers(2) == reaper_2_mock
    assert controller.reapers(3) == reaper_2_mock
    
    controller.removeReaper(reaper_2_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 1
    assert controller.indexByReaper(reaper_1_mock) == 0
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 1
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_3_mock
    assert controller.reapers(2) == reaper_2_mock
    assert controller.reapers(3) == reaper_2_mock

    exception_tester("reaper is not exist", controller.removeReaper, reaper_2_mock, {'from': deployer})

    controller.removeReaper(reaper_3_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 0
    assert controller.indexByReaper(reaper_1_mock) == 0
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 0
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_3_mock
    assert controller.reapers(2) == reaper_2_mock
    assert controller.reapers(3) == reaper_2_mock

    controller.addReaper(reaper_1_mock, {'from': deployer})
    assert controller.lastReaperIndex() == 1
    assert controller.indexByReaper(reaper_1_mock) == 1
    assert controller.indexByReaper(reaper_2_mock) == 0
    assert controller.indexByReaper(reaper_3_mock) == 0
    assert controller.reapers(0) == ZERO_ADDRESS
    assert controller.reapers(1) == reaper_1_mock
    assert controller.reapers(2) == reaper_2_mock
    assert controller.reapers(3) == reaper_2_mock
