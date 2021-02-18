def test_complex_v7(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 1000100)
    usdn_token.deposit(accounts[1], 1)
    usdn_token.stake(100)
    assert usdn_token.balanceOf(accounts[0]) == 1000100
    assert usdn_token.balanceOf(accounts[1]) == 1
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 1000101

    usdn_token.transfer(accounts[2], 500050, {'from': accounts[0]})
    usdn_token.stake(100)
    assert usdn_token.balanceOf(accounts[0]) == 500099
    assert usdn_token.balanceOf(accounts[1]) == 1
    assert usdn_token.balanceOf(accounts[2]) == 500099
    assert usdn_token.totalSupply() == 1000201

    usdn_token.deposit(accounts[0], 1000000000000)
    usdn_token.withdraw(accounts[2])
    assert usdn_token.balanceOf(accounts[0]) == 1000000500099
    assert usdn_token.balanceOf(accounts[1]) == 1
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 1000000500102

    usdn_token.stake(500000000000)
    assert usdn_token.balanceOf(accounts[0]) == 1499997500710
    assert usdn_token.balanceOf(accounts[1]) == 999897
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 1500000500102

    usdn_token.withdraw(accounts[1])
    usdn_token.transfer(accounts[1], 1125000375017, {'from': accounts[0]})
    assert usdn_token.balanceOf(accounts[0]) == 374997125693
    assert usdn_token.balanceOf(accounts[1]) == 1125000375017
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 1499999500205

    usdn_token.stake(500000000000)
    assert usdn_token.balanceOf(accounts[0]) == 499996209239
    assert usdn_token.balanceOf(accounts[1]) == 1500000624970
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 1999999500205

    usdn_token.withdraw(accounts[0])
    usdn_token.withdraw(accounts[1])
    usdn_token.stake(500000000000)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 0
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 500002665996
