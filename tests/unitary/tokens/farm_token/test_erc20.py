def test_erc20(farm_token, erc20_tester):
    erc20_tester(contract=farm_token, name="Dispersion Farm Token",
                 symbol="DSP", decimals=18, initial_supply=100_000 * 10 ** 18)
