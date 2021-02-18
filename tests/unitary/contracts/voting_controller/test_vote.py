# #!/usr/bin/python3

# import brownie
# import pytest
# from brownie.test import given, strategy

# WEEK = 604800

# @given(amount=strategy('uint256', min_value=1, max_value=10**3))
# def test_vote_simple(voting_controller, farm_token, three_reapers_stub, neo, morpheus, amount):
#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': morpheus})

#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': neo})

#     initial_balance = farm_token.balanceOf(neo)
#     farm_token.approve(voting_controller, amount, {'from': neo})
#     tx1 = voting_controller.vote(
#         three_reapers_stub[0], farm_token, amount, {'from': neo})

#     assert tx1.return_value is None
#     assert len(tx1.events) == 2
#     assert tx1.events["Transfer"].values() == [neo, voting_controller, amount]
#     assert tx1.events["Vote"].values(
#     ) == [three_reapers_stub[0], farm_token, neo, amount]

#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': neo})

#     assert farm_token.balanceOf(neo) == initial_balance - amount
#     assert farm_token.balanceOf(voting_controller) == amount
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == amount
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == amount
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == amount
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0

#     with brownie.reverts("tokens are locked"):
#         voting_controller.unvote(
#             three_reapers_stub[0], farm_token, amount, {'from': neo})

#     brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == amount

#     tx2 = voting_controller.unvote(
#         three_reapers_stub[0], farm_token, amount, {'from': neo})

#     assert tx2.return_value is None
#     assert len(tx2.events) == 2
#     assert tx2.events["Transfer"].values() == [voting_controller, neo, amount]
#     assert tx2.events["Unvote"].values(
#     ) == [three_reapers_stub[0], farm_token, neo, amount]

#     assert farm_token.balanceOf(neo) == initial_balance
#     assert farm_token.balanceOf(voting_controller) == 0
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == 0
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == 0
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0


# @given(amount=strategy('uint256', min_value=1, max_value=10**3))
# def test_vote_delegated(voting_controller, farm_token, three_reapers_stub, neo, morpheus, trinity, amount):
#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': morpheus})

#     with brownie.reverts():
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, {'from': neo})

#     with brownie.reverts("voting approve required"):
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     with brownie.reverts("voting approve required"):
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, morpheus, {'from': neo})

#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, morpheus, neo)

#     tx1 = voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, True, {'from': neo})
#     assert voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, morpheus, neo)

#     initial_balance = farm_token.balanceOf(neo)
#     farm_token.approve(voting_controller, 2*amount, {'from': neo})

#     voting_controller.vote(
#         three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     assert farm_token.balanceOf(neo) == initial_balance - amount
#     assert farm_token.balanceOf(voting_controller) == amount
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == amount
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == amount
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0 # amount
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == amount

#     tx2 = voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, False, {'from': neo})
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)

#     with brownie.reverts("voting approve required"):
#         voting_controller.vote(
#             three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     with brownie.reverts("voting approve required"):
#         voting_controller.unvote(
#             three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, True, {'from': neo})
#     assert voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)

#     voting_controller.vote(
#         three_reapers_stub[0], farm_token, amount, neo, {'from': morpheus})

#     assert farm_token.balanceOf(neo) == initial_balance - 2*amount
#     assert farm_token.balanceOf(voting_controller) == 2*amount
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == 2*amount
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == 2*amount
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == 2*amount

#     with brownie.reverts("tokens are locked"):
#         voting_controller.unvote(
#             three_reapers_stub[0], farm_token, 2*amount, neo, {'from': morpheus})

#     brownie.chain.mine(1, brownie.chain.time()+WEEK+1)

#     voting_controller.unvote(
#         three_reapers_stub[0], farm_token, 2*amount, neo, {'from': morpheus})

#     assert farm_token.balanceOf(neo) == initial_balance
#     assert farm_token.balanceOf(voting_controller) == 0
#     assert voting_controller.reaperBalances(
#         three_reapers_stub[0], farm_token) == 0
#     assert voting_controller.balances(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.availableToUnvote(
#         three_reapers_stub[0], farm_token, neo) == 0
#     assert voting_controller.accountVotePower(
#         three_reapers_stub[0], neo) == 0

#     voting_controller.voteApprove(
#         three_reapers_stub[0], farm_token, morpheus, False, {'from': neo})
#     assert not voting_controller.voteAllowance(
#         three_reapers_stub[0], farm_token, neo, morpheus)

#     assert tx1.return_value is None
#     assert len(tx1.events) == 1
#     assert tx1.events["VoteApproval"].values(
#     ) == [three_reapers_stub[0], farm_token, neo, morpheus, True]

#     assert tx2.return_value is None
#     assert len(tx2.events) == 1
#     assert tx2.events["VoteApproval"].values(
#     ) == [three_reapers_stub[0], farm_token, neo, morpheus, False]
