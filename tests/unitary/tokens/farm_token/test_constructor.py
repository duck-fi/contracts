from brownie.test import given, strategy


def test_init_token(farm_token, deployer, morpheus, trinity, oracle, ZERO_ADDRESS):
    assert farm_token.name() == "Dispersion Farm Token"
    assert farm_token.symbol() == "DSP"
    assert farm_token.decimals() == 18

    assert farm_token.totalSupply() == 100_000 * 10 ** 18
    assert farm_token.balanceOf(deployer) == farm_token.totalSupply()
    assert farm_token.balanceOf(morpheus) == 0
    assert farm_token.balanceOf(trinity) == 0
    assert farm_token.balanceOf(oracle) == 0
    assert farm_token.minter() == ZERO_ADDRESS
    assert farm_token.owner() == deployer


def test_initial_balances(farm_token, deployer):
    @given(account=strategy('address', exclude=deployer))
    def test_balance_is_zero(account):
        assert farm_token.balanceOf(account) == 0
    test_balance_is_zero()
