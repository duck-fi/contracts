def test_burnable(farm_token, erc20_burnable_tester):
    erc20_burnable_tester(contract=farm_token)
