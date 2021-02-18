import brownie


def test_transfer_huge_amount(usdn_token, neo, morpheus):
    usdn_token.deposit(neo, 1)

    with brownie.reverts("Integer underflow"):
        usdn_token.transfer(morpheus, 2)


def test_transfer(usdn_token, neo, morpheus):
    usdn_token.transfer(morpheus, 1)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.balanceOf(morpheus) == 1
    assert usdn_token.totalSupply() == 1


def test_transfer_after_deposit(usdn_token, neo, morpheus):
    usdn_token.deposit(neo, 2)

    assert usdn_token.balanceOf(neo) == 2
    assert usdn_token.balanceOf(morpheus) == 1

    usdn_token.transfer(morpheus, 2)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.balanceOf(morpheus) == 3
    assert usdn_token.totalSupply() == 3


def test_transfer_after_staking_reward(usdn_token, neo, morpheus):
    usdn_token.stake(1)

    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.balanceOf(morpheus) == 3
    assert usdn_token.totalSupply() == 3

    usdn_token.transfer(neo, 3, {'from': morpheus})

    assert usdn_token.balanceOf(neo) == 3
    assert usdn_token.balanceOf(morpheus) == 0
    assert usdn_token.totalSupply() == 3


def test_transfer_before_staking_reward(usdn_token, neo, morpheus, trinity):
    usdn_token.transfer(morpheus, 2)

    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 2
    assert usdn_token.balanceOf(trinity) == 0

    usdn_token.stake(2)

    assert usdn_token.totalSupply() == 5
    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 3


def test_transferFrom(usdn_token, neo, morpheus, trinity):
    usdn_token.approve(morpheus, 1)

    assert usdn_token.allowance(neo, morpheus) == 1

    usdn_token.transferFrom(neo, morpheus, 1, {'from': morpheus})

    assert usdn_token.totalSupply() == 5
    assert usdn_token.balanceOf(neo) == 0
    assert usdn_token.balanceOf(morpheus) == 4
    assert usdn_token.balanceOf(trinity) == 0


def test_transferFrom_allowance(usdn_token, neo, morpheus):
    usdn_token.approve(neo, 1, {'from': morpheus})

    assert usdn_token.allowance(morpheus, neo) == 1

    usdn_token.transferFrom(morpheus, neo, 1)

    assert usdn_token.totalSupply() == 5
    assert usdn_token.balanceOf(neo) == 1
    assert usdn_token.balanceOf(morpheus) == 3

    usdn_token.approve(neo, 1, {'from': morpheus})
    assert usdn_token.allowance(morpheus, neo) == 1

    usdn_token.approve(neo, 0, {'from': morpheus})
    assert usdn_token.allowance(morpheus, neo) == 0
