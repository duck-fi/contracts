def test_without_reaper_strategy(reaper, deployer):
    reaper.reap({'from': deployer})


def test_without_reaper_strategy_any_account(reaper, thomas):
    reaper.reap({'from': thomas})


def test_with_mock(reaper, reaper_strategy_mock, deployer, thomas):
    assert reaper_strategy_mock.isReapCalled() == False
    reaper.setReaperStrategy(reaper_strategy_mock, {'from': deployer})
    assert reaper.reaperStrategy() == reaper_strategy_mock
    reaper.reap({'from': deployer})
    assert reaper_strategy_mock.isReapCalled() == True
