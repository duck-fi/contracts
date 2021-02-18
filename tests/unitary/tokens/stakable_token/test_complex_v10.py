def test_complex_v10(usdn_token, accounts):
    usdn_token.deposit(accounts[0], 10 * 10 ** 18)
    usdn_token.transfer(accounts[1], 2 * 10 ** 18)
    usdn_token.transfer(accounts[2], 3 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 5000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 3000000000000000000
    assert usdn_token.totalSupply() == 10000000000000000000

    usdn_token.deposit(accounts[0], 5 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 10000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 3000000000000000000
    assert usdn_token.totalSupply() == 15000000000000000000

    usdn_token.deposit(accounts[3], 1 * 10 ** 18)
    usdn_token.deposit(accounts[4], 1 * 10 ** 18)
    usdn_token.deposit(accounts[5], 1 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 10000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 1000000000000000000
    assert usdn_token.totalSupply() == 18000000000000000000

    usdn_token.stake(9 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 10000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 1000000000000000000
    assert usdn_token.totalSupply() == 18000000000000000000

    usdn_token.deposit(accounts[5], 7 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 10000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 1000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 8000000000000000000
    assert usdn_token.totalSupply() == 25000000000000000000

    usdn_token.transfer(accounts[3], 1 * 10 ** 18)
    usdn_token.transfer(accounts[4], 1 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 8000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 2000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 8000000000000000000
    assert usdn_token.totalSupply() == 25000000000000000000

    usdn_token.stake(9 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 12000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 8500000000000000000
    assert usdn_token.totalSupply() == 34000000000000000000

    usdn_token.deposit(accounts[0], 5 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 17000000000000000000
    assert usdn_token.balanceOf(accounts[1]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 8500000000000000000
    assert usdn_token.totalSupply() == 39000000000000000000

    usdn_token.withdraw(accounts[0])
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 3000000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 8500000000000000000
    assert usdn_token.totalSupply() == 22000000000000000000

    usdn_token.stake(11 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 6750000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 12750000000000000000
    assert usdn_token.totalSupply() == 33000000000000000000

    usdn_token.deposit(accounts[5], 7 * 10 ** 18)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 6750000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 19750000000000000000
    assert usdn_token.totalSupply() == 40000000000000000000

    usdn_token.transfer(accounts[1], 65 * 10 ** 17, {'from': accounts[5]})
    usdn_token.transfer(accounts[2], 625 * 10 ** 16, {'from': accounts[5]})
    usdn_token.transfer(accounts[3], 1 * 10 ** 18, {'from': accounts[5]})
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 11000000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 13000000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 5500000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 4500000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 6000000000000000000
    assert usdn_token.totalSupply() == 40000000000000000000

    usdn_token.stake(165 * 10 ** 17)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 13250000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 19250000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 8250000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 6750000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 9000000000000000000
    assert usdn_token.totalSupply() == 56500000000000000000

    usdn_token.stake(565 * 10 ** 16)
    assert usdn_token.balanceOf(accounts[0]) == 0
    assert usdn_token.balanceOf(accounts[1]) == 14575000000000000000
    assert usdn_token.balanceOf(accounts[2]) == 21175000000000000000
    assert usdn_token.balanceOf(accounts[3]) == 9075000000000000000
    assert usdn_token.balanceOf(accounts[4]) == 7425000000000000000
    assert usdn_token.balanceOf(accounts[5]) == 9900000000000000000
    assert usdn_token.totalSupply() == 62150000000000000000
