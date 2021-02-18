def test_transfer_to_transfable_account(strict_transfable_token, deployer, morpheus):
    strict_transfable_token.mint(morpheus, 1, {'from': deployer})
    tx = strict_transfable_token.transfer(deployer, 1, {'from': morpheus})
    assert strict_transfable_token.balanceOf(deployer) == 1
    assert strict_transfable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [morpheus, deployer, 1]


def test_transfer_from_transfable_account(strict_transfable_token, thomas, deployer):
    tx = strict_transfable_token.transfer(thomas, 1, {'from': deployer})
    assert strict_transfable_token.balanceOf(deployer) == 0
    assert strict_transfable_token.balanceOf(thomas) == 1
    assert strict_transfable_token.totalSupply() == 1
    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [deployer, thomas, 1]


def test_not_transferable_transfer(strict_transfable_token, exception_tester, trinity, thomas):
    exception_tester("strict transfer",
                     strict_transfable_token.transfer, trinity, 1, {'from': thomas})


def test_transfer_to_zero(strict_transfable_token, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("recipient is zero address",
                     strict_transfable_token.transfer, ZERO_ADDRESS, 0, {'from': deployer})


def test_transfer_underflow(strict_transfable_token, exception_tester, deployer, thomas):
    exception_tester("Integer underflow",
                     strict_transfable_token.transfer, deployer, 1_000, {'from': thomas})


def test_transfer_cant_mint(strict_transfable_token, exception_tester, trinity, deployer):
    exception_tester("Integer underflow",
                     strict_transfable_token.transfer, trinity, 1_000, {'from': deployer})
