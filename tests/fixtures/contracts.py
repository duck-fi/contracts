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
def reaper_controller_stub(VotingController, ReaperControllerStub, neo, three_reapers_stub):
    contract = ReaperControllerStub.deploy({'from': neo})
    contract.addReaper(three_reapers_stub[0])
    contract.addReaper(three_reapers_stub[1])
    contract.addReaper(three_reapers_stub[2])

    yield contract


@pytest.fixture(scope="module")
def voting_strategy_stub(VotingStrategyStub, neo):
    yield VotingStrategyStub.deploy({'from': neo})


@pytest.fixture(scope="module")
def voting_controller(VotingController, reaper_controller_stub, neo, accounts):
    yield VotingController.deploy(reaper_controller_stub, {'from': neo})
