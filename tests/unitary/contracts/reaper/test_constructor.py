def test_init(reaper, controller, voting_controller, boosting_controller_mocked, lp_token, farm_token, MAX_UINT256):
    assert reaper.votingController() == voting_controller
    assert reaper.boostingController() == boosting_controller_mocked
    assert reaper.lpToken() == lp_token
    assert reaper.farmToken() == farm_token
    assert reaper.adminFee() == 0
    assert farm_token.allowance(reaper, controller) == 0
