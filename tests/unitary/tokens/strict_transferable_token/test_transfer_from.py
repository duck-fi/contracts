def test_transfer_from(strict_transferable_token, deployer, morpheus):
    strict_transferable_token.mint(deployer, 1, {'from': deployer})
    tx = strict_transferable_token.transferFrom(
        deployer, morpheus, 1, {'from': deployer})
    assert strict_transferable_token.balanceOf(morpheus) == 1
    assert strict_transferable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [deployer, morpheus, 1]


def test_transfer_from_between_not_transfable_account_from_transfable(exception_tester, strict_transferable_token, deployer, thomas, morpheus):
    exception_tester("Integer underflow",
                     strict_transferable_token.transferFrom, morpheus, thomas, 1_000, {'from': deployer})


def test_transfer_from_between_not_transfable_account_from_transfable(strict_transferable_token, deployer, thomas, morpheus):
    tx = strict_transferable_token.transferFrom(
        morpheus, thomas, 1, {'from': deployer})
    assert strict_transferable_token.balanceOf(thomas) == 1
    assert strict_transferable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [morpheus, thomas, 1]


def test_transfer_from_cant_mint(strict_transferable_token, exception_tester, deployer, thomas, trinity):
    exception_tester("Integer underflow",
                     strict_transferable_token.transferFrom, thomas, trinity, 1_000, {'from': deployer})


def test_not_transferable_transfer(strict_transferable_token, exception_tester, trinity, thomas):
    exception_tester("strict transfer",
                     strict_transferable_token.transferFrom, thomas, trinity, 1, {'from': thomas})


def test_transfer_from_from_zero(strict_transferable_token, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("sender is zero address",
                     strict_transferable_token.transferFrom, ZERO_ADDRESS, ZERO_ADDRESS, 0, {'from': deployer})


def test_transfer_from_to_zero(strict_transferable_token, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("recipient is zero address",
                     strict_transferable_token.transferFrom, deployer, ZERO_ADDRESS, 0, {'from': deployer})
