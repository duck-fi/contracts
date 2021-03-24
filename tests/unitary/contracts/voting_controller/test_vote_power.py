import math


def test_reaper_vote_share_init(voting_controller_mocked, reaper_1_mock, reaper_2_mock, reaper_3_mock):
    assert voting_controller_mocked.reaperVotePower(reaper_1_mock) == 0
    assert voting_controller_mocked.reaperVotePower(reaper_2_mock) == 0
    assert voting_controller_mocked.reaperVotePower(reaper_3_mock) == 0
    assert voting_controller_mocked.totalVotePower() == 0
    assert voting_controller_mocked.voteIntegral(reaper_1_mock).return_value == 0
    assert voting_controller_mocked.voteIntegral(reaper_2_mock).return_value == 0
    assert voting_controller_mocked.voteIntegral(reaper_3_mock).return_value == 0


def test_not_valid_reaper(exception_tester, voting_controller_mocked):
    exception_tester(
        "invalid reaper", voting_controller_mocked.reaperVotePower, voting_controller_mocked)
    exception_tester(
        "invalid reaper", voting_controller_mocked.voteIntegral, voting_controller_mocked)


def test_reaper_vote_share(exception_tester, voting_controller_mocked, farm_token, neo, morpheus, trinity, thomas, reaper_1_mock, reaper_2_mock, reaper_3_mock, week, chain):
    farm_token.transfer(morpheus, 2000, {'from': neo})
    farm_token.transfer(trinity, 2000, {'from': neo})
    farm_token.transfer(thomas, 2000, {'from': neo})
    initial_balance = farm_token.balanceOf(neo)

    farm_token.approve(voting_controller_mocked, 2000, {'from': neo})
    farm_token.approve(voting_controller_mocked, 2000, {'from': morpheus})
    farm_token.approve(voting_controller_mocked, 2000, {'from': trinity})
    farm_token.approve(voting_controller_mocked, 2000, {'from': thomas})

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 10, {'from': neo})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 20, {'from': neo})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 30, {'from': neo})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 40, {'from': neo})
    assert farm_token.balanceOf(neo) == initial_balance - 100
    assert farm_token.balanceOf(voting_controller_mocked) == 100

    assert voting_controller_mocked.reaperVotePower(
        reaper_1_mock) == 10
    assert voting_controller_mocked.reaperVotePower(
        reaper_2_mock) == 20
    assert voting_controller_mocked.reaperVotePower(
        reaper_3_mock) == 70
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, neo) == 10
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, neo) == 20
    assert voting_controller_mocked.accountVotePower(reaper_3_mock, neo) == 70

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 10, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 20, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 30, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 40, {'from': morpheus})

    assert voting_controller_mocked.reaperVotePower(
        reaper_1_mock) == 20
    assert voting_controller_mocked.reaperVotePower(
        reaper_2_mock) == 40
    assert voting_controller_mocked.reaperVotePower(
        reaper_3_mock) == 140
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, neo) == 10
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, neo) == 20
    assert voting_controller_mocked.accountVotePower(reaper_3_mock, neo) == 70
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, morpheus) == 10
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, morpheus) == 20
    assert voting_controller_mocked.accountVotePower(
        reaper_3_mock, morpheus) == 70

    tx_voting = voting_controller_mocked.startVoting()
    chain.mine(1, voting_controller_mocked.nextSnapshotTimestamp() - 100)

    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_3_mock) == 0
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_2_mock) == 0
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastVotes(
        reaper_3_mock) == 333333333333333333
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 333333333333333333
    assert voting_controller_mocked.lastVotes(
        reaper_3_mock) == 333333333333333333
    assert math.fabs(voting_controller_mocked.voteIntegral(
        reaper_1_mock) == 333333333333333333 * (chain.time() - tx_voting.timestamp)) < 1_000
    assert math.fabs(voting_controller_mocked.voteIntegral(
        reaper_2_mock) == 333333333333333333 * (chain.time() - tx_voting.timestamp)) < 1_000
    assert math.fabs(voting_controller_mocked.voteIntegral(
        reaper_3_mock) == 333333333333333333 * (chain.time() - tx_voting.timestamp)) < 1_000


    chain.mine(1, voting_controller_mocked.nextSnapshotTimestamp() + 1)
    snapshot_timestamp = voting_controller_mocked.nextSnapshotTimestamp()
    voting_controller_mocked.snapshot()
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(1, chain.time() + week - 100)

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 20
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 40
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 140
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_1_mock) == 333333333333333333 * (snapshot_timestamp - tx_voting.timestamp)
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_2_mock) == 333333333333333333 * (snapshot_timestamp - tx_voting.timestamp)
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_3_mock) == 333333333333333333 * (snapshot_timestamp - tx_voting.timestamp)
    assert voting_controller_mocked.lastVotes(
        reaper_1_mock) == 1 * 10 ** 17
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 2 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 7 * 10 ** 17
    assert voting_controller_mocked.reaperVotePower(
        reaper_1_mock) == 20
    assert voting_controller_mocked.reaperVotePower(
        reaper_2_mock) == 40
    assert voting_controller_mocked.reaperVotePower(
        reaper_3_mock) == 140

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 30, {'from': neo})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 10, {'from': neo})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 60, {'from': neo})

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 50
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 50
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 200
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, neo) == 40
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, neo) == 30
    assert voting_controller_mocked.accountVotePower(
        reaper_3_mock, neo) == 130
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, morpheus) == 10
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, morpheus) == 20
    assert voting_controller_mocked.accountVotePower(
        reaper_3_mock, morpheus) == 70

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 50, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 50, {'from': morpheus})
    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 100
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 100
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 200
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, neo) == 40
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, neo) == 30
    assert voting_controller_mocked.accountVotePower(
        reaper_3_mock, neo) == 130
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, morpheus) == 60
    assert voting_controller_mocked.accountVotePower(
        reaper_2_mock, morpheus) == 70
    assert voting_controller_mocked.accountVotePower(
        reaper_3_mock, morpheus) == 70

    assert voting_controller_mocked.reaperVotePower(
        reaper_1_mock) == 100
    assert voting_controller_mocked.reaperVotePower(
        reaper_2_mock) == 100
    assert voting_controller_mocked.reaperVotePower(
        reaper_3_mock) == 200

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 1000, {'from': morpheus})
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, morpheus) == 1060
    assert voting_controller_mocked.reaperVotePower(reaper_1_mock) == 1100
    assert voting_controller_mocked.reaperVotePower(reaper_2_mock) <= 100
    assert voting_controller_mocked.reaperVotePower(reaper_3_mock) == 200
    assert voting_controller_mocked.reaperVotePower(reaper_1_mock) + voting_controller_mocked.reaperVotePower(
        reaper_2_mock) + voting_controller_mocked.reaperVotePower(reaper_3_mock) == 1400

    exception_tester("tokens are locked", voting_controller_mocked.unvote,
                     reaper_1_mock, farm_token, 1000, {'from': morpheus})

    chain.mine(1, chain.time() + week + 1)
    voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, 1000, {'from': morpheus})
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, morpheus) == 60
    assert voting_controller_mocked.reaperVotePower(
        reaper_1_mock) == 100
    assert voting_controller_mocked.reaperVotePower(
        reaper_2_mock) == 100
    assert voting_controller_mocked.reaperVotePower(
        reaper_3_mock) == 200

    assert voting_controller_mocked.lastVotes(
        reaper_1_mock) == 1 * 10 ** 17
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 2 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 7 * 10 ** 17

    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperVotePower(
        reaper_1_mock) == 100
    assert voting_controller_mocked.reaperVotePower(
        reaper_2_mock) == 100
    assert voting_controller_mocked.reaperVotePower(
        reaper_3_mock) == 200

    assert voting_controller_mocked.lastVotes(
        reaper_1_mock) == 2.5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 2.5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 5 * 10 ** 17
