def test_not_owner(voting_controller_mocked, ownable_exception_tester, ZERO_ADDRESS, thomas):
    ownable_exception_tester(
        voting_controller_mocked.setVotingToken, ZERO_ADDRESS, {'from': thomas})


def test_set_zero_address(voting_controller_mocked, exception_tester, ZERO_ADDRESS, deployer):
    exception_tester("zero address", voting_controller_mocked.setVotingToken,
                     ZERO_ADDRESS, {'from': deployer})


def test_set_once(exception_tester, voting_controller_mocked, deployer, voting_token_mocked, thomas):
    assert voting_controller_mocked.votingToken() == voting_token_mocked
    exception_tester("set only once", voting_controller_mocked.setVotingToken,
                     thomas, {'from': deployer})
