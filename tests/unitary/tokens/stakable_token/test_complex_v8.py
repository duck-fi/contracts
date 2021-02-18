def test_complex_v8(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 5 * 10 ** 18)
    usdn_token.transfer(accounts[1], 1 * 10 ** 18)
    usdn_token.deposit(accounts[0], 5 * 10 ** 18)
    assert usdn_token.totalSupply() == 10000000000000000000

    usdn_token.stake(4 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 9000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 10000000000000000000
    
    usdn_token.stake(4 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 12600000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 1400000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 0
    assert usdn_token.totalSupply() == 14000000000000000000
