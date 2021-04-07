import brownie


def test_not_by_owner(farm_token, thomas, exception_tester):
    exception_tester("minter only", farm_token.startEmission, {'from': thomas})


def test_success_startEmission(farm_token, voting_controller, controller, reaper_1_mock, deployer, chain):
    t1 = chain.time()
    controller.addReaper(reaper_1_mock) # need to have at least 1 reaper to start emission (launch voting)
    controller.startEmission(voting_controller, 0, {'from': deployer})
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()
    startEmissionTimestamp = farm_token.startEmissionTimestamp()
    t2 = chain.time()

    assert lastEmissionUpdateTimestamp >= t1 and lastEmissionUpdateTimestamp <= t2
    assert startEmissionTimestamp >= t1 and startEmissionTimestamp <= t2


def test_fail_double_startEmission(controller, voting_controller, deployer, exception_tester):
    exception_tester("", controller.startEmission,
                     voting_controller, 0, {'from': deployer})
