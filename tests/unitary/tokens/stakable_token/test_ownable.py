import brownie


def test_ownable_not_owner(usdn_token, neo, morpheus):
    with brownie.reverts("only owner or admin"):
        usdn_token.deposit(neo, 1, {'from': morpheus})


def test_ownable_transfer_ownership_not_owner(usdn_token, thomas, morpheus):
    with brownie.reverts("only owner"):
        usdn_token.transferOwnership(morpheus, {'from': thomas})


def test_ownable_set_admin_not_owner(usdn_token, thomas, morpheus):
    with brownie.reverts("only owner or admin"):
        usdn_token.setAdmin(morpheus, {'from': thomas})


def test_ownable_transfer_ownership(usdn_token, neo, morpheus, deployer):
    usdn_token.transferOwnership(morpheus, {'from': deployer})
    usdn_token.deposit(neo, 1, {'from': morpheus})

    assert usdn_token.totalSupply() == 1
    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 0


def test_ownable_set_admin(usdn_token, thomas, morpheus, trinity):
    usdn_token.setAdmin(trinity, {'from': morpheus})
    # check succes setAdmin by admin
    usdn_token.setAdmin(trinity, {'from': trinity})
    usdn_token.deposit(thomas, 1, {'from': trinity})

    assert usdn_token.totalSupply() == 2
    assert usdn_token.balanceOf(thomas) == 1
    assert usdn_token.balanceOf(morpheus) == 0
