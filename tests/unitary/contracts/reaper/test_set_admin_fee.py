def test_not_owner(reaper, ownable_exception_tester, thomas):
    ownable_exception_tester(
        reaper.setAdminFee, 0, {'from': thomas})


def test_greater_max(reaper, exception_tester, deployer):
    exception_tester("adminFee > 100%", reaper.setAdminFee,
                     10 ** 3 + 1, {'from': deployer})


def test_success(reaper, deployer):
    assert reaper.adminFee() == 0
    reaper.setAdminFee(10 ** 3, {'from': deployer})  # 100%
    assert reaper.adminFee() == 10 ** 3
    reaper.setAdminFee(10 ** 2, {'from': deployer})  # 10%
    assert reaper.adminFee() == 10 ** 2
