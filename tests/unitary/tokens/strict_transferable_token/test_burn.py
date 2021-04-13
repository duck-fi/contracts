def test_burnable(strict_transferable_token, erc20_burnable_tester):
    erc20_burnable_tester(contract=strict_transferable_token)
