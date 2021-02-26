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
def controller_mock(ControllerMock, deployer, reaper_1_mock, reaper_2_mock, reaper_3_mock):
    contract = ControllerMock.deploy({'from': deployer})
    contract.addReaper(reaper_1_mock)
    contract.addReaper(reaper_2_mock)
    contract.addReaper(reaper_3_mock)
    yield contract


@pytest.fixture(scope="module")
def controller(Controller, farm_token, deployer, gas_token_check_list):
    yield Controller.deploy(farm_token, gas_token_check_list, {'from': deployer})


@pytest.fixture(scope="module")
def reaper(Reaper, lp_token, farm_token, controller, voting_controller, boosting_controller, deployer, gas_token_check_list):
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


@pytest.fixture(scope="module")
def voting_controller_mocked(VotingController, controller_mock, farm_token, deployer, gas_token_check_list):
    yield VotingController.deploy(controller_mock, gas_token_check_list, farm_token, {'from': deployer})


@pytest.fixture(scope="module")
def boosting_controller(BoostingController, farm_token, gas_token_check_list, deployer):
    yield BoostingController.deploy(farm_token, gas_token_check_list, {'from': deployer})


@pytest.fixture(scope="module")
def boosting_controller_mocked(BoostingController, farm_token, gas_token_check_list, deployer):
    yield BoostingController.deploy(farm_token, gas_token_check_list, {'from': deployer})


@pytest.fixture(scope="module")
def initial_emission_distributor(InitialEmissionDistributor, farm_token, deployer, gas_token_check_list):
    yield InitialEmissionDistributor.deploy(farm_token, gas_token_check_list, {'from': deployer})


@pytest.fixture(scope="module")
def addresses_check_list(AddressesCheckList, deployer):
    yield AddressesCheckList.deploy({'from': deployer})


@pytest.fixture(scope="module")
def gas_token_check_list(AddressesCheckList, deployer, chi_token):
    check_list = AddressesCheckList.deploy({'from': deployer})
    check_list.set(chi_token, True, {'from': deployer})
    yield check_list


@pytest.fixture(scope="module")
def voting_white_list(AddressesCheckList, deployer):
    check_list = AddressesCheckList.deploy({'from': deployer})
    check_list.set(deployer, True, {'from': deployer})
    yield check_list


@pytest.fixture(scope="module")
def boosting_white_list(AddressesCheckList, deployer):
    check_list = AddressesCheckList.deploy({'from': deployer})
    check_list.set(deployer, True, {'from': deployer})
    yield check_list


@pytest.fixture(scope="module")
def white_list(AddressesCheckList, deployer):
    check_list = AddressesCheckList.deploy({'from': deployer})
    check_list.set(deployer, True, {'from': deployer})
    yield check_list
