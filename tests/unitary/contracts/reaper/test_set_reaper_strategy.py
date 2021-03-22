def test_not_owner(reaper, ownable_exception_tester, ZERO_ADDRESS, thomas):
    ownable_exception_tester(
        reaper.setReaperStrategy, ZERO_ADDRESS, {'from': thomas})


def test_success(reaper, deployer, thomas, MAX_UINT256, lp_token):
    reaper.setReaperStrategy(thomas, {'from': deployer})
    assert reaper.reaperStrategy() == thomas
    assert reaper.depositAllowance(reaper, thomas) == MAX_UINT256
    assert lp_token.allowance(reaper, thomas) == MAX_UINT256
