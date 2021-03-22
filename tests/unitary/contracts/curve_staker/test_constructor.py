def test_init(curve_staker_mocked, lp_token, crv_token_mock, curve_gauge_mock, curve_ve_mock, year, deployer):
    assert curve_staker_mocked.stakeToken() == lp_token
    assert curve_staker_mocked.rewardToken() == crv_token_mock
    assert curve_staker_mocked.stakeContract() == curve_gauge_mock
    assert curve_staker_mocked.votingEscrowContract() == curve_ve_mock
    assert curve_staker_mocked.lockingPeriod() == year
