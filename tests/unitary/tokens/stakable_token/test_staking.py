import brownie


def test_staking_ownership(usdn_token, morpheus):
    with brownie.reverts("owner or admin only"):
        usdn_token.stake(1, {'from': morpheus})


def test_staking_equal_amounts(usdn_token, neo, morpheus, trinity):
    assert usdn_token.totalSupply() == 0

    usdn_token.deposit(neo, 10 ** 12)
    usdn_token.deposit(morpheus, 10 ** 12)
    usdn_token.deposit(trinity, 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)

    assert usdn_token.totalSupply() == 3000000000000
    assert usdn_token.balanceOf(neo) == 1000000000000
    assert usdn_token.balanceOf(morpheus) == 1000000000000
    assert usdn_token.balanceOf(trinity) == 1000000000000


def test_staking_many(usdn_token, neo, morpheus, trinity):
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)
    usdn_token.stake(3 * 10 ** 12)

    assert usdn_token.totalSupply() == 33000000000000
    assert usdn_token.balanceOf(neo) == 10999999999982
    assert usdn_token.balanceOf(morpheus) == 10999999999982
    assert usdn_token.balanceOf(trinity) == 10999999999982


def test_staking(usdn_token, neo, morpheus, trinity, thomas):
    usdn_token.deposit(thomas, 26 * 10 ** 12)

    assert usdn_token.totalSupply() == 59000000000000
    assert usdn_token.balanceOf(neo) == 10999999999982
    assert usdn_token.balanceOf(morpheus) == 10999999999982
    assert usdn_token.balanceOf(trinity) == 10999999999982
    assert usdn_token.balanceOf(thomas) == 26000000000000

    usdn_token.stake(6 * 10 ** 12)

    assert usdn_token.totalSupply() == 65000000000000
    assert usdn_token.balanceOf(neo) == 12999999999976
    assert usdn_token.balanceOf(morpheus) == 12999999999976
    assert usdn_token.balanceOf(trinity) == 12999999999976
    assert usdn_token.balanceOf(thomas) == 26000000000000


def test_staking_huge_reward(usdn_token, neo, morpheus, trinity, thomas):
    usdn_token.stake(6000 * 10 ** 12)
    assert usdn_token.totalSupply() == 6065000000000000
    assert usdn_token.balanceOf(neo) == 1212999999997756
    assert usdn_token.balanceOf(morpheus) == 1212999999997756
    assert usdn_token.balanceOf(trinity) == 1212999999997756
    assert usdn_token.balanceOf(thomas) == 2425999999999990
