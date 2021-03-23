def test_invest_zero(reaper, deployer):
    reaper.invest({'from': deployer})


def test_invest_without_reaper_strategy(reaper, deployer, lp_token):
    lp_token.transfer(reaper, 1, {'from': deployer})
    reaper.invest({'from': deployer})


def test_with_mock(reaper, reaper_strategy_mock, deployer, lp_token):
    assert reaper_strategy_mock.isReapCalled() == False
    reaper.setReaperStrategy(reaper_strategy_mock, {'from': deployer})
    assert reaper.reaperStrategy() == reaper_strategy_mock
    reaper.invest({'from': deployer})
    assert reaper_strategy_mock.isInvestCalled() == True
    assert lp_token.balanceOf(reaper) == 0
    assert lp_token.balanceOf(reaper_strategy_mock) == 1
