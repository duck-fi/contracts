import brownie


def test_not_owner_or_admin_deposit(usdn_token, neo, morpheus):
    with brownie.reverts("only owner or admin"):
        usdn_token.deposit(neo, 1, {'from': morpheus})


def test_zero_deposit(usdn_token, thomas):
    with brownie.reverts("amount is 0"):
        usdn_token.deposit(thomas, 0)


def test_deposit(usdn_token, neo, morpheus):
    usdn_token.deposit(neo, 1)
    usdn_token.deposit(morpheus, 2)

    assert usdn_token.totalSupply() == 3
    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 2


def test_deposit_many(usdn_token, neo, morpheus, trinity):
    usdn_token.deposit(trinity, 1)
    usdn_token.deposit(trinity, 2)
    usdn_token.deposit(trinity, 3)

    assert usdn_token.totalSupply() == 9
    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 2
    assert usdn_token.balanceOf(trinity) == 6
