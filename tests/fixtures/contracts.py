import pytest


@pytest.fixture(scope="module")
def reaper_1_mock(accounts):
    yield accounts[10]


@pytest.fixture(scope="module")
def reaper_2_mock(accounts):
    yield accounts[11]


@pytest.fixture(scope="module")
def reaper_3_mock(accounts):
    yield accounts[12]


@pytest.fixture(scope="module")
def proxy_deployer(ProxyDeployer, deployer):
    yield ProxyDeployer.deploy({'from': deployer})


@pytest.fixture(scope="module")
def reaper_mock(ReaperMock, lp_token, farm_token, deployer):
    yield ReaperMock.deploy(lp_token, farm_token, {'from': deployer})


@pytest.fixture(scope="module")
def controller_mock(ControllerMock, deployer, reaper_1_mock, reaper_2_mock, reaper_3_mock):
    contract = ControllerMock.deploy({'from': deployer})
    contract.addReaper(reaper_1_mock)
    contract.addReaper(reaper_2_mock)
    contract.addReaper(reaper_3_mock)
    yield contract


@pytest.fixture(scope="module")
def controller(Controller, gas_token_check_list, farm_token, deployer):
    controller = Controller.deploy(
        farm_token, gas_token_check_list, {'from': deployer})
    farm_token.setMinter(controller, {'from': deployer})
    yield controller


@pytest.fixture(scope="module")
def reaper(Reaper, lp_token, farm_token, controller, voting_controller, boosting_controller, deployer, gas_token_check_list):
    contract = Reaper.deploy(lp_token, farm_token, controller, voting_controller,
                             boosting_controller, gas_token_check_list, 0, {'from': deployer})
    controller.addReaper(contract)
    yield contract


@pytest.fixture(scope="module")
def reaper_2(Reaper, lp_token, farm_token, controller, voting_controller, boosting_controller, deployer, gas_token_check_list):
    contract = Reaper.deploy(lp_token, farm_token, controller, voting_controller,
                             boosting_controller, gas_token_check_list, 0, {'from': deployer})
    controller.addReaper(contract)
    yield contract


@pytest.fixture(scope="module")
def reaper_strategy_mock(ReaperStrategyMock, reaper, lp_token, deployer):
    yield ReaperStrategyMock.deploy(lp_token, reaper, {'from': deployer})


@pytest.fixture(scope="module")
def voting_controller(VotingController, controller, farm_token, deployer, gas_token_check_list):
    yield VotingController.deploy(controller, gas_token_check_list, farm_token, {'from': deployer})


@ pytest.fixture(scope="module")
def voting_controller_mocked(VotingController, controller_mock, farm_token, deployer, gas_token_check_list):
    yield VotingController.deploy(controller_mock, gas_token_check_list, farm_token, {'from': deployer})


@ pytest.fixture(scope="module")
def boosting_controller(BoostingController, farm_token, gas_token_check_list, deployer):
    yield BoostingController.deploy(farm_token, gas_token_check_list, {'from': deployer})


@ pytest.fixture(scope="module")
def boosting_controller_mocked(BoostingController, farm_token, gas_token_check_list, deployer):
    yield BoostingController.deploy(farm_token, gas_token_check_list, {'from': deployer})


@ pytest.fixture(scope="module")
def voting_controller_mocked(VotingController, controller_mock, farm_token, deployer, gas_token_check_list):
    yield VotingController.deploy(controller_mock, gas_token_check_list, farm_token, {'from': deployer})


@ pytest.fixture(scope="module")
def boosting_controller(BoostingController, gas_token_check_list, deployer):
    yield BoostingController.deploy(gas_token_check_list, {'from': deployer})


@ pytest.fixture(scope="module")
def boosting_controller_mocked(BoostingController, gas_token_check_list, deployer):
    yield BoostingController.deploy(gas_token_check_list, {'from': deployer})


@ pytest.fixture(scope="module")
def reaper_reward_distributor_mocked(ReaperRewardDistributor, reaper_mock, gas_token_check_list, deployer):
    yield ReaperRewardDistributor.deploy(reaper_mock, gas_token_check_list, {'from': deployer})


@ pytest.fixture(scope="module")
def initial_emission_distributor(InitialEmissionDistributor, farm_token, deployer, gas_token_check_list):
    yield InitialEmissionDistributor.deploy(farm_token, gas_token_check_list, {'from': deployer})


@ pytest.fixture(scope="module")
def addresses_check_list(WhiteList, deployer):
    yield WhiteList.deploy({'from': deployer})


@ pytest.fixture(scope="module")
def gas_token_check_list(WhiteList, deployer, chi_token):
    check_list = WhiteList.deploy({'from': deployer})
    check_list.addAddress(chi_token, {'from': deployer})
    yield check_list


@ pytest.fixture(scope="module")
def voting_white_list(WhiteList, deployer):
    check_list = WhiteList.deploy({'from': deployer})
    check_list.addAddress(deployer, {'from': deployer})
    yield check_list


@ pytest.fixture(scope="module")
def boosting_white_list(WhiteList, deployer):
    check_list = WhiteList.deploy({'from': deployer})
    check_list.addAddress(deployer, {'from': deployer})
    yield check_list


@ pytest.fixture(scope="module")
def white_list(WhiteList, deployer):
    check_list = WhiteList.deploy({'from': deployer})
    check_list.addAddress(deployer, {'from': deployer})
    yield check_list


@ pytest.fixture(scope="module")
def curve_minter_mock(CurveMinterMock, crv_token_mock, deployer):
    yield CurveMinterMock.deploy(crv_token_mock, {'from': deployer})


@ pytest.fixture(scope="module")
def curve_gauge_mock(CurveGaugeMock, curve_minter_mock, crv_token_mock, lp_token, deployer):
    yield CurveGaugeMock.deploy(curve_minter_mock, lp_token, crv_token_mock, {'from': deployer})


@ pytest.fixture(scope="module")
def curve_ve_mock(CurveVEMock, crv_token_mock, deployer):
    yield CurveVEMock.deploy(crv_token_mock, {'from': deployer})


@ pytest.fixture(scope="module")
def curve_staker_mocked(CurveStaker, curve_ve_mock, curve_gauge_mock, crv_token_mock, lp_token, deployer):
    contract = CurveStaker.deploy(
        curve_gauge_mock, lp_token, crv_token_mock, curve_ve_mock, {'from': deployer})
    lp_token.approve(curve_gauge_mock, 2 ** 256 - 1,
                     {'from': contract})  # TODO: max int
    yield contract
