# #!/usr/bin/python3

# import brownie
# import pytest
# from brownie.test import given, strategy

# WEEK = 604800

# # TODO: make test for farm token and voting token
# @given(amount=strategy('uint256', min_value=1, max_value=10**3))
# def test_set_strategy(voting_controller, farm_token, usdn_token, voting_token, three_reapers_stub, neo, morpheus, amount):
#     # set up usdn_token for voting
#     farm_token.transfer(morpheus, 5*amount, {'from': neo})
#     voting_token.transfer(morpheus, 5*amount, {'from': neo})

#     initial_balance = farm_token.balanceOf(neo)
#     initial_balance_voting = voting_token.balanceOf(neo)

#     usdn_token.deposit(neo, initial_balance, {'from': neo})
#     usdn_token.approve(voting_controller, 5*amount, {'from': neo})

#     voting_token.approve(voting_controller, 5*amount, {'from': neo})
#     farm_token.approve(voting_controller, 5*amount, {'from': neo})
#     voting_token.approve(voting_controller, 5*amount, {'from': morpheus})
#     farm_token.approve(voting_controller, 5*amount, {'from': morpheus})

#     # try to vote with usdn_token (it fails, invalid coin)
#     with brownie.reverts("invalid coin"):
#         voting_controller.vote(three_reapers_stub[0], usdn_token, amount, {'from': neo})

#     # try to vote with farm_token (success)
#     voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': neo})
#     assert farm_token.balanceOf(voting_controller) == amount
#     assert farm_token.balanceOf(neo) == initial_balance - amount

#     # check for vote shares
#     assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 18
#     assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 0

#     # try to unvote with farm_token (locked)
#     with brownie.reverts("tokens are locked"):
#         voting_controller.unvote(three_reapers_stub[0], farm_token, amount, {'from': neo})

#     brownie.chain.mine(2, None, WEEK+1)
#     voting_controller.unvote(three_reapers_stub[0], farm_token, amount, {'from': neo})
#     assert farm_token.balanceOf(voting_controller) == 0
#     assert initial_balance == farm_token.balanceOf(neo)

#     # check for vote shares
#     assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 0
#     assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 0

#     # vote with voting_token
#     voting_controller.vote(three_reapers_stub[0], voting_token, amount, {'from': neo})
#     assert voting_token.balanceOf(voting_controller) == amount
#     assert initial_balance_voting - amount == voting_token.balanceOf(neo)
#     assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 18
#     assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 2 * amount # amount is increased by 2 (rate=2)
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 0

#     # vote with farm_token for morpheus
#     voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': morpheus})
#     assert farm_token.balanceOf(voting_controller) == amount
#     assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 18
#     assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 3 * amount # amount is increased by 3 (rate=3)
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 1 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 0

#     # vote with farm_token for morpheus
#     voting_controller.vote(three_reapers_stub[0], farm_token, amount, {'from': morpheus})
#     assert farm_token.balanceOf(voting_controller) == 2 * amount
#     assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 18
#     assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 3 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 2 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 0

#     # vote with farm_token
#     voting_controller.vote(three_reapers_stub[0], farm_token, 3*amount, {'from': morpheus})
#     assert farm_token.balanceOf(voting_controller) == 5 * amount
#     assert voting_controller.reaperVotePower(three_reapers_stub[0]) == 1 * 10 ** 18
#     assert voting_controller.reaperVotePower(three_reapers_stub[1]) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 3 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 5 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 0

#     # vote with voting_token
#     voting_controller.vote(three_reapers_stub[1], voting_token, 2 * amount, {'from': neo})
#     assert farm_token.balanceOf(voting_controller) == 5 * amount
#     assert voting_token.balanceOf(voting_controller) == 3 * amount
#     assert 5.71 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[0]) and voting_controller.reaperVotePower(three_reapers_stub[0]) <= 5.72 * 10 ** 17
#     assert 4.28 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[1]) and voting_controller.reaperVotePower(three_reapers_stub[1]) <= 4.29 * 10 ** 17
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 3 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 6 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 5 * amount
#     assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 0

#     # vote with voting_token
#     voting_controller.vote(three_reapers_stub[1], voting_token, 3 * amount, {'from': morpheus})
#     assert farm_token.balanceOf(voting_controller) == 5 * amount
#     assert voting_token.balanceOf(voting_controller) == 6 * amount
#     assert voting_controller.reaperBalances(three_reapers_stub[0], farm_token) == 5
#     assert voting_controller.reaperBalances(three_reapers_stub[0], voting_token) == 1
#     assert voting_controller.reaperBalances(three_reapers_stub[1], farm_token) == 0
#     assert voting_controller.reaperBalances(three_reapers_stub[1], voting_token) == 5
    
#     # farm_weight = 1, voting_weight = 2+2*(5/(5+6)) = ~2.90909090909
    
#     assert voting_controller.balances(three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.balances(three_reapers_stub[0], voting_token, neo) == 1
#     assert voting_controller.accountVotePower(three_reapers_stub[0], neo) == 2 * amount

#     assert voting_controller.balances(three_reapers_stub[1], farm_token, neo) == 0
#     assert voting_controller.balances(three_reapers_stub[1], voting_token, neo) == 2
#     assert voting_controller.accountVotePower(three_reapers_stub[1], neo) == 5 * amount

#     assert voting_controller.balances(three_reapers_stub[0], farm_token, morpheus) == 5
#     assert voting_controller.balances(three_reapers_stub[0], voting_token, morpheus) == 0
#     assert voting_controller.accountVotePower(three_reapers_stub[0], morpheus) == 5 * amount

#     assert voting_controller.balances(three_reapers_stub[1], farm_token, morpheus) == 0
#     assert voting_controller.balances(three_reapers_stub[1], voting_token, morpheus) == 3
#     assert voting_controller.accountVotePower(three_reapers_stub[1], morpheus) == 8 * amount

#     # three_reapers_stub[0]_weight = 7, three_reapers_stub[1] = 13, sum = 20

#     assert 3.33 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[0]) and voting_controller.reaperVotePower(three_reapers_stub[0]) <= 3.34 * 10 ** 17
#     assert 6.66 * 10 ** 17 <= voting_controller.reaperVotePower(three_reapers_stub[1]) and voting_controller.reaperVotePower(three_reapers_stub[1]) <= 6.67 * 10 ** 17
