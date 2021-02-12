def test_init(usdn_token, deployer, ZERO_ADDRESS):
    assert usdn_token.name() == "Neutrino USD"
    assert usdn_token.symbol() == "USDN"
    assert usdn_token.decimals() == 18
    assert usdn_token.owner() == deployer
    assert usdn_token.admin() == ZERO_ADDRESS
    assert usdn_token.isDeprecated() == False
    assert usdn_token.balanceOf(deployer) == 0
    assert usdn_token.totalSupply() == 0
    assert usdn_token.percents(0) == 10 ** 12
    assert usdn_token.percentsLength() == 1
