def test_init(reaper, controller, voting_controller, lp_token, farm_token, MAX_UINT256):
    assert reaper.controller() == controller
    assert reaper.votingController() == voting_controller
    assert reaper.lpToken() == lp_token
    assert reaper.farmToken() == farm_token
    assert reaper.adminFee() == 0
    assert farm_token.allowance(reaper, controller) == MAX_UINT256
