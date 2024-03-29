def test_mint_not_minter(strict_transferable_token, thomas, exception_tester):
    exception_tester("minter only", strict_transferable_token.mint,
                     thomas, 1, {'from': thomas})


def test_mint_zero_address(ZERO_ADDRESS, strict_transferable_token, deployer, exception_tester):
    exception_tester("zero address", strict_transferable_token.mint,
                     ZERO_ADDRESS, 1, {'from': deployer})


def test_mint(strict_transferable_token, deployer, morpheus, ZERO_ADDRESS):
    tx = strict_transferable_token.mint(morpheus, 1_000, {'from': deployer})
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [
        ZERO_ADDRESS, morpheus, 1_000]
    assert strict_transferable_token.totalSupply() == 1_000
    assert strict_transferable_token.balanceOf(morpheus) == 1_000
    assert strict_transferable_token.balanceOf(deployer) == 0
