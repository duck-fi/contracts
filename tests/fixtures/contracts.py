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
def controller_stub(VotingController, ControllerStub, deployer, three_reapers_stub):
    contract = ControllerStub.deploy({'from': deployer})
    contract.addReaper(three_reapers_stub[0])
    contract.addReaper(three_reapers_stub[1])
    contract.addReaper(three_reapers_stub[2])

    yield contract


@pytest.fixture(scope="module")
def voting_controller(VotingController, controller_stub, farm_token, voting_token, deployer, accounts):
    yield VotingController.deploy(controller_stub, farm_token, voting_token, {'from': deployer})
