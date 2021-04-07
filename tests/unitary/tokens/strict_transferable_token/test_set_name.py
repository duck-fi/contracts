def test_not_owner(strict_transferable_token, morpheus, ownable_exception_tester):
    ownable_exception_tester(strict_transferable_token.setName, 'Test',
                             'TST', {'from': morpheus})


def test_set_name(strict_transferable_token, deployer):
    strict_transferable_token.setName('Test token', 'TSTS', {'from': deployer})
    assert strict_transferable_token.name() == "Test token"
    assert strict_transferable_token.symbol() == "TSTS"
