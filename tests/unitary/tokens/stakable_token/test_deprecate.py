import brownie


def test_deprecate(usdn_token, neo, morpheus):
    usdn_token.deprecate()

    with brownie.reverts("deprecated"):
        usdn_token.deposit(neo, 1)

    with brownie.reverts("deprecated"):
        usdn_token.stake(1)

    with brownie.reverts("deprecated"):
        usdn_token.withdraw(neo)

    with brownie.reverts("deprecated"):
        usdn_token.transfer(morpheus, 2)

    with brownie.reverts("deprecated"):
        usdn_token.transferFrom(morpheus, morpheus, 2)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.totalSupply() == 0
