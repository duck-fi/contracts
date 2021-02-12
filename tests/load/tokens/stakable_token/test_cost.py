def test_cost_deposit(usdn_token, trinity):
    for i in range(0, 100):
        usdn_token.deposit(trinity, 1)


def test_cost_stake(usdn_token):
    for i in range(0, 100):
        usdn_token.stake(1)


def test_cost_transfer(usdn_token, neo, trinity):
    for i in range(0, 100):
        usdn_token.transfer(neo, 1, {'from': trinity})
