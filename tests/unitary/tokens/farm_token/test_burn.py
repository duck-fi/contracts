def test_erc20(farm_token, erc20_burnable_tester):
    erc20_burnable_tester(contract=farm_token)
