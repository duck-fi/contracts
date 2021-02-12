import brownie


def test_ownable_not_owner(usdn_token, neo, morpheus):
    with brownie.reverts("only owner or admin"):
        usdn_token.deposit(neo, 1, {'from': morpheus})


def test_ownable_transfer_ownership(usdn_token, neo, morpheus):
    usdn_token.transferOwnership(morpheus)
    usdn_token.deposit(neo, 1)

    assert usdn_token.totalSupply() == 1
    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 0
