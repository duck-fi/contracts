import brownie


def test_not_by_owner(farm_token, thomas):
    with brownie.reverts("owner only"):
        farm_token.startEmission({'from': thomas})


def test_success_startEmission(farm_token, deployer, chain):
    t1 = chain.time()
    farm_token.startEmission({'from': deployer})
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()
    startEmissionTimestamp = farm_token.startEmissionTimestamp()
    t2 = chain.time()

    assert lastEmissionUpdateTimestamp >= t1 and lastEmissionUpdateTimestamp <= t2
    assert startEmissionTimestamp >= t1 and startEmissionTimestamp <= t2


def test_fail_double_startEmission(farm_token, deployer):
    with brownie.reverts("emission already started"):
        farm_token.startEmission({'from': deployer})
