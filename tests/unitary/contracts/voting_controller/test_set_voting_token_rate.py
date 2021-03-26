def test_not_owner(voting_controller_mocked, ownable_exception_tester, thomas):
    ownable_exception_tester(
        voting_controller_mocked.setVotingTokenRate, 1, 1, {'from': thomas})


def test_set_zero_rate(voting_controller_mocked, exception_tester, deployer):
    exception_tester("can't be equal zero", voting_controller_mocked.setVotingTokenRate,
                     0, 1, {'from': deployer})


def test_set_zero_rate_amplifier(voting_controller_mocked, exception_tester, deployer):
    exception_tester("can't be equal zero", voting_controller_mocked.setVotingTokenRate,
                     1, 0, {'from': deployer})


def test_success(voting_controller_mocked, deployer):
    voting_controller_mocked.setVotingTokenRate(10, 100, {'from': deployer})
    assert voting_controller_mocked.votingTokenRate() == 10
    assert voting_controller_mocked.votingTokenRateAmplifier() == 100
