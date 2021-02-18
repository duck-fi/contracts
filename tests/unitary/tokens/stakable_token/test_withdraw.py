import brownie


def test_withdraw_not_owner(usdn_token, morpheus):
    with brownie.reverts("owner or admin only"):
        usdn_token.withdraw(morpheus, {'from': morpheus})


def test_withdraw(usdn_token, neo):
    usdn_token.deposit(neo, 1)

    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.totalSupply() == 1

    usdn_token.withdraw(neo)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.totalSupply() == 0


def test_withdraw_after_deposit(usdn_token, neo):
    usdn_token.deposit(neo, 2)

    assert usdn_token.balanceOf(neo) == 2
    assert usdn_token.totalSupply() == 2

    usdn_token.withdraw(neo)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.totalSupply() == 0


def test_withdraw_after_staking_reward(usdn_token, neo):
    usdn_token.deposit(neo, 1)
    usdn_token.stake(1)
    usdn_token.withdraw(neo)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.totalSupply() == 0


def test_withdraw_complex(usdn_token, neo):
    usdn_token.deposit(neo, 2)
    assert usdn_token.balanceOf(neo) == 2

    usdn_token.stake(2)
    assert usdn_token.balanceOf(neo) == 2

    usdn_token.withdraw(neo)
    assert usdn_token.totalSupply() == 0
    assert usdn_token.balanceOf(neo) == 0
