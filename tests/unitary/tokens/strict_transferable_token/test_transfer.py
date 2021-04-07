def test_transfer_to_transfable_account(strict_transferable_token, deployer, morpheus):
    strict_transferable_token.mint(morpheus, 1, {'from': deployer})
    tx = strict_transferable_token.transfer(deployer, 1, {'from': morpheus})
    assert strict_transferable_token.balanceOf(deployer) == 1
    assert strict_transferable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [morpheus, deployer, 1]


def test_transfer_from_transfable_account(strict_transferable_token, thomas, deployer):
    tx = strict_transferable_token.transfer(thomas, 1, {'from': deployer})
    assert strict_transferable_token.balanceOf(deployer) == 0
    assert strict_transferable_token.balanceOf(thomas) == 1
    assert strict_transferable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [deployer, thomas, 1]


def test_not_transferable_transfer(strict_transferable_token, exception_tester, trinity, thomas):
    exception_tester("strict transfer",
                     strict_transferable_token.transfer, trinity, 1, {'from': thomas})


def test_transfer_to_zero(strict_transferable_token, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("recipient is zero address",
                     strict_transferable_token.transfer, ZERO_ADDRESS, 0, {'from': deployer})


def test_transfer_underflow(strict_transferable_token, exception_tester, deployer, thomas):
    exception_tester("Integer underflow",
                     strict_transferable_token.transfer, deployer, 1_000, {'from': thomas})


def test_transfer_cant_mint(strict_transferable_token, exception_tester, trinity, deployer):
    exception_tester("Integer underflow",
                     strict_transferable_token.transfer, trinity, 1_000, {'from': deployer})
