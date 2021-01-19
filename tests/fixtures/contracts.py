import pytest


@pytest.fixture(scope="module")
def voting_controller(VotingController, neo):
    yield VotingController.deploy(neo, {'from': neo})
