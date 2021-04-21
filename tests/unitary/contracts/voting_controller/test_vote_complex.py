import math
from brownie.test import given, strategy


MULTIPLIER = 10 ** 18
FARM_TOKEN_RATE = 1
VOTING_TOKEN_RATE = 2
VOTING_TOKEN_RATE_AMPLIFIER = 2
VOTING_TOKEN_RATE_MODIFIED = 10
VOTING_TOKEN_RATE_AMPLIFIER_MODIFIED = 5


def check_reapers_vote_power(voting_controller, controller):
    power = 0
    for i in range(1, controller.lastReaperIndex()):
        check_reaper_vote_power(voting_controller, controller.reapers(i))
        power += voting_controller.reaperVotePower(controller.reapers(i))

    if voting_controller.coinBalances(voting_controller.farmToken()) + voting_controller.coinBalances(voting_controller.votingToken()):
        assert MULTIPLIER >= power * MULTIPLIER / \
            voting_controller.totalVotePower() >= 0.999 * MULTIPLIER
    else:
        assert power == 0


def check_reapers_vote_power_modified(voting_controller, controller):
    power = 0
    for i in range(1, controller.lastReaperIndex()):
        check_reaper_vote_power_modified(voting_controller, controller.reapers(i))
        power += voting_controller.reaperVotePower(controller.reapers(i))

    if voting_controller.coinBalances(voting_controller.farmToken()) + voting_controller.coinBalances(voting_controller.votingToken()):
        assert MULTIPLIER >= power * MULTIPLIER / \
            voting_controller.totalVotePower() >= 0.999 * MULTIPLIER
    else:
        assert power == 0


def check_reaper_vote_power(voting_controller, reaper):
    _farmTokenBalance = voting_controller.coinBalances(
        voting_controller.farmToken())
    _votingTokenBalance = voting_controller.coinBalances(
        voting_controller.votingToken())

    if _farmTokenBalance + _votingTokenBalance == 0:
        assert voting_controller.reaperVotePower(reaper) == 0
        return

    _votingTokenRate = math.floor(MULTIPLIER * VOTING_TOKEN_RATE + math.floor(MULTIPLIER *
                                                                              VOTING_TOKEN_RATE_AMPLIFIER * _farmTokenBalance /
                                                                              (_farmTokenBalance + _votingTokenBalance)))
    _reaperVoteBalance = math.floor(voting_controller.reaperBalances(
        reaper, voting_controller.votingToken()) * _votingTokenRate / MULTIPLIER) + math.floor(voting_controller.reaperBalances(reaper, voting_controller.farmToken()) * FARM_TOKEN_RATE)
    assert math.fabs(voting_controller.reaperVotePower(
        reaper) - _reaperVoteBalance) < 10 ** 2


def check_reaper_vote_power_modified(voting_controller, reaper):
    _farmTokenBalance = voting_controller.coinBalances(
        voting_controller.farmToken())
    _votingTokenBalance = voting_controller.coinBalances(
        voting_controller.votingToken())

    if _farmTokenBalance + _votingTokenBalance == 0:
        assert voting_controller.reaperVotePower(reaper) == 0
        return

    _votingTokenRate = math.floor(MULTIPLIER * VOTING_TOKEN_RATE_MODIFIED + math.floor(MULTIPLIER *
                                                                                       VOTING_TOKEN_RATE_AMPLIFIER_MODIFIED * _farmTokenBalance /
                                                                                       (_farmTokenBalance + _votingTokenBalance)))
    _reaperVoteBalance = math.floor(voting_controller.reaperBalances(
        reaper, voting_controller.votingToken()) * _votingTokenRate / MULTIPLIER) + math.floor(voting_controller.reaperBalances(reaper, voting_controller.farmToken()) * FARM_TOKEN_RATE)
    assert math.fabs(voting_controller.reaperVotePower(
        reaper) - _reaperVoteBalance) < 10 ** 2


def check_account_reapers_vote_power(voting_controller, controller, account):
    share = 0
    for i in range(1, controller.lastReaperIndex()):
        check_account_vote_power(
            voting_controller, controller.reapers(i), account)
        share += voting_controller.accountVotePower(
            controller.reapers(i), account)

    if voting_controller.coinBalances(voting_controller.farmToken()) + voting_controller.coinBalances(voting_controller.votingToken()):
        assert MULTIPLIER >= share
    else:
        assert share == 0


def check_account_vote_power(voting_controller, reaper, account):
    _farmTokenBalance = voting_controller.coinBalances(
        voting_controller.farmToken())
    _votingTokenBalance = voting_controller.coinBalances(
        voting_controller.votingToken())

    if _farmTokenBalance + _votingTokenBalance == 0:
        assert voting_controller.accountVotePower(reaper, account) == 0
        return

    _votingTokenRate = math.floor(MULTIPLIER * VOTING_TOKEN_RATE + math.floor(MULTIPLIER *
                                                                              VOTING_TOKEN_RATE_AMPLIFIER * _farmTokenBalance /
                                                                              (_farmTokenBalance + _votingTokenBalance)))
    _accountVoteBalance = math.floor(voting_controller.balances(
        reaper, voting_controller.votingToken(), account) * _votingTokenRate / MULTIPLIER) + math.floor(voting_controller.balances(reaper, voting_controller.farmToken(), account) * FARM_TOKEN_RATE)
    assert math.fabs(voting_controller.accountVotePower(
        reaper, account) - _accountVoteBalance) < 10 ** 2


@given(amount=strategy('uint256', min_value=10 ** 10, max_value=10 ** 18))
def test_vote_complex(exception_tester, voting_controller_mocked, controller_mock, farm_token, voting_token_mocked, reaper_1_mock, reaper_2_mock, deployer, morpheus, amount, chain, week):
    # set up usdn_token for voting
    farm_token.transfer(morpheus, 5 * amount, {'from': deployer})
    voting_token_mocked.mint(morpheus, 5 * amount, {'from': deployer})
    voting_token_mocked.mint(deployer, 5 * amount, {'from': deployer})

    initial_balance = farm_token.balanceOf(deployer)
    initial_balance_voting = voting_token_mocked.balanceOf(deployer)

    farm_token.approve(voting_controller_mocked, 5 *
                       amount, {'from': deployer})
    farm_token.approve(voting_controller_mocked, 5 *
                       amount, {'from': morpheus})

    # try to vote with farm_token (success)
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, amount, {'from': deployer})
    assert farm_token.balanceOf(voting_controller_mocked) == amount
    assert farm_token.balanceOf(deployer) == initial_balance - amount

    # check for vote shares
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, deployer) == amount
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, deployer) == 0

    # try to unvote with farm_token (locked)
    exception_tester("tokens are locked", voting_controller_mocked.unvote,
                     reaper_1_mock, farm_token, amount, {'from': deployer})

    chain.mine(2, None, week + 1)
    voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, amount, {'from': deployer})
    assert farm_token.balanceOf(voting_controller_mocked) == 0
    assert initial_balance == farm_token.balanceOf(deployer)

    # check for vote shares
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)

    # vote with voting_token
    voting_controller_mocked.vote(
        reaper_1_mock, voting_token_mocked, amount, {'from': deployer})
    assert voting_token_mocked.balanceOf(voting_controller_mocked) == amount
    assert initial_balance_voting - \
        amount == voting_token_mocked.balanceOf(deployer)
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)

    # vote with farm_token for morpheus
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, amount, {'from': morpheus})
    assert farm_token.balanceOf(voting_controller_mocked) == amount
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    # vote with farm_token for morpheus
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, amount, {'from': morpheus})
    assert farm_token.balanceOf(voting_controller_mocked) == 2 * amount
    assert voting_token_mocked.balanceOf(
        voting_controller_mocked) == 1 * amount
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    # vote with farm_token
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 3*amount, {'from': morpheus})
    assert farm_token.balanceOf(voting_controller_mocked) == 5 * amount
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    # vote with voting_token
    voting_controller_mocked.vote(
        reaper_2_mock, voting_token_mocked, 2 * amount, {'from': deployer})
    assert farm_token.balanceOf(voting_controller_mocked) == 5 * amount
    assert voting_token_mocked.balanceOf(
        voting_controller_mocked) == 3 * amount
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    # vote with voting_token
    voting_controller_mocked.vote(
        reaper_2_mock, voting_token_mocked, 3 * amount, {'from': morpheus})
    assert farm_token.balanceOf(voting_controller_mocked) == 5 * amount
    assert voting_token_mocked.balanceOf(
        voting_controller_mocked) == 6 * amount
    check_reapers_vote_power(voting_controller_mocked, controller_mock)
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 0
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, voting_token_mocked) == 5 * amount

    # farm_weight = 1, voting_weight = 2+2*(5/(5+6)) = ~2.90909090909

    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, deployer) == 0
    assert voting_controller_mocked.balances(
        reaper_1_mock, voting_token_mocked, deployer) == 1 * amount
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    assert voting_controller_mocked.balances(
        reaper_2_mock, farm_token, deployer) == 0
    assert voting_controller_mocked.balances(
        reaper_2_mock, voting_token_mocked, deployer) == 2 * amount
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, morpheus) == 5 * amount
    assert voting_controller_mocked.balances(
        reaper_1_mock, voting_token_mocked, morpheus) == 0
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    assert voting_controller_mocked.balances(
        reaper_2_mock, farm_token, morpheus) == 0
    assert voting_controller_mocked.balances(
        reaper_2_mock, voting_token_mocked, morpheus) == 3 * amount
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, deployer)
    check_account_reapers_vote_power(voting_controller_mocked,
                                     controller_mock, morpheus)

    # reaper_1_mock_weight = 7, reaper_2_mock_weight = 13, sum = 20

    check_reapers_vote_power(voting_controller_mocked, controller_mock)

    # now change voting token rate
    chain.mine(1, chain.time() + week + 100)

    voting_controller_mocked.setVotingTokenRate(
        VOTING_TOKEN_RATE_MODIFIED, VOTING_TOKEN_RATE_AMPLIFIER_MODIFIED, {'from': deployer})

    check_reapers_vote_power_modified(
        voting_controller_mocked, controller_mock)
