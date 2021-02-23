def test_not_owner(strict_transfable_token, morpheus, ownable_exception_tester):
    ownable_exception_tester(strict_transfable_token.setName, 'Test',
                             'TST', {'from': morpheus})


def test_set_name(strict_transfable_token, deployer):
    strict_transfable_token.setName('Test token', 'TSTS', {'from': deployer})
    assert strict_transfable_token.name() == "Test token"
    assert strict_transfable_token.symbol() == "TSTS"
