def test_not_owner(addresses_check_list, ownable_exception_tester, ZERO_ADDRESS, thomas):
    ownable_exception_tester(
        addresses_check_list.addAddress, ZERO_ADDRESS, {'from': thomas})


def test_set_zero_address(addresses_check_list, exception_tester, ZERO_ADDRESS, deployer):
    exception_tester("zero address", addresses_check_list.addAddress,
                     ZERO_ADDRESS, {'from': deployer})


def test_success_set(addresses_check_list, deployer):
    addresses_check_list.removeAddress(deployer, {'from': deployer})
    assert not addresses_check_list.check(deployer)
    addresses_check_list.addAddress(deployer, {'from': deployer})
    assert addresses_check_list.check(deployer)
