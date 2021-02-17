def test_not_owner(farm_token, morpheus, ownable_exception_tester):
    ownable_exception_tester(farm_token.setName, 'Test',
                             'TST', {'from': morpheus})


def test_set_name(farm_token, deployer):
    farm_token.setName('Test token', 'TSTS', {'from': deployer})
    assert farm_token.name() == "Test token"
    assert farm_token.symbol() == "TSTS"
