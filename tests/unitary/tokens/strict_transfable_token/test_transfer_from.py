def test_transfer_from(strict_transfable_token, deployer, morpheus):
    strict_transfable_token.mint(deployer, 1, {'from': deployer})
    tx = strict_transfable_token.transferFrom(
        deployer, morpheus, 1, {'from': deployer})
    assert strict_transfable_token.balanceOf(morpheus) == 1
    assert strict_transfable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [deployer, morpheus, 1]


def test_transfer_from_between_not_transfable_account_from_transfable(exception_tester, strict_transfable_token, deployer, thomas, morpheus):
    exception_tester("Integer underflow",
                     strict_transfable_token.transferFrom, morpheus, thomas, 1_000, {'from': deployer})


def test_transfer_from_between_not_transfable_account_from_transfable(strict_transfable_token, deployer, thomas, morpheus):
    tx = strict_transfable_token.transferFrom(
        morpheus, thomas, 1, {'from': deployer})
    assert strict_transfable_token.balanceOf(thomas) == 1
    assert strict_transfable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [morpheus, thomas, 1]


def test_transfer_from_cant_mint(strict_transfable_token, exception_tester, deployer, thomas, trinity):
    exception_tester("Integer underflow",
                     strict_transfable_token.transferFrom, thomas, trinity, 1_000, {'from': deployer})


def test_not_transferable_transfer(strict_transfable_token, exception_tester, trinity, thomas):
    exception_tester("strict transfer",
                     strict_transfable_token.transferFrom, thomas, trinity, 1, {'from': thomas})


def test_transfer_from_from_zero(strict_transfable_token, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("sender is zero address",
                     strict_transfable_token.transferFrom, ZERO_ADDRESS, ZERO_ADDRESS, 0, {'from': deployer})


def test_transfer_from_to_zero(strict_transfable_token, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("recipient is zero address",
                     strict_transfable_token.transferFrom, deployer, ZERO_ADDRESS, 0, {'from': deployer})
