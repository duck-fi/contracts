import pytest


@pytest.fixture(scope="module")
def three_reapers_stub(accounts):
    contracts = [
        accounts[10],
        accounts[11],
        accounts[12],
    ]

    yield contracts


@pytest.fixture(scope="module")
def controller_stub(ControllerStub, deployer, three_reapers_stub):
    contract = ControllerStub.deploy({'from': deployer})
    contract.addReaper(three_reapers_stub[0])
    contract.addReaper(three_reapers_stub[1])
    contract.addReaper(three_reapers_stub[2])

    yield contract


@pytest.fixture(scope="module")
def voting_controller(VotingController, controller_stub, farm_token, deployer, gas_token_check_list):
    yield VotingController.deploy(controller_stub, gas_token_check_list, farm_token, {'from': deployer})


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
def white_list(AddressesCheckList, deployer):
    check_list = AddressesCheckList.deploy({'from': deployer})
    check_list.set(deployer, True, {'from': deployer})
    yield check_list
