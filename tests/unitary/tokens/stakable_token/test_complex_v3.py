def test_complex_v3(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 100)
    usdn_token.deposit(accounts[1], 1)
    usdn_token.deposit(accounts[2], 1)
    assert usdn_token.totalSupply() == 102

    usdn_token.stake(102)
    assert usdn_token.balanceOf(accounts[0]) == 100
    assert usdn_token.balanceOf(accounts[1]) == 1
    assert usdn_token.balanceOf(accounts[2]) == 1
    assert usdn_token.totalSupply() == 102

    usdn_token.stake(102)
    assert usdn_token.balanceOf(accounts[0]) == 200
    assert usdn_token.balanceOf(accounts[1]) == 2
    assert usdn_token.balanceOf(accounts[2]) == 2

    usdn_token.withdraw(accounts[0])
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 2
    assert usdn_token.balanceOf(accounts[2]) == 2
    assert usdn_token.totalSupply() == 4

    usdn_token.stake(4)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 4
    assert usdn_token.balanceOf(accounts[2]) == 4
    assert usdn_token.totalSupply() == 8
