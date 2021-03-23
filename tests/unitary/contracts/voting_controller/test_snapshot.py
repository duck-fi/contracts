INIT_TIME = 1609372800


def test_snapshot(exception_tester, voting_controller_mocked, farm_token, deployer, morpheus, trinity, thomas, reaper_1_mock, reaper_2_mock, reaper_3_mock, chain, week, day):
    farm_token.transfer(morpheus, 1000, {'from': deployer})
    farm_token.transfer(trinity, 1000, {'from': deployer})
    farm_token.transfer(thomas, 1000, {'from': deployer})
    initial_balance = farm_token.balanceOf(deployer)

    farm_token.approve(voting_controller_mocked, 2000, {'from': deployer})
    farm_token.approve(voting_controller_mocked, 2000, {'from': morpheus})
    farm_token.approve(voting_controller_mocked, 2000, {'from': trinity})
    farm_token.approve(voting_controller_mocked, 2000, {'from': thomas})

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 10, {'from': deployer})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 20, {'from': deployer})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 30, {'from': deployer})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 40, {'from': deployer})
    assert farm_token.balanceOf(deployer) == initial_balance - 100
    assert farm_token.balanceOf(voting_controller_mocked) == 100

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 10
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 20
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 70
    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, deployer) == 10
    assert voting_controller_mocked.balances(
        reaper_2_mock, farm_token, deployer) == 20
    assert voting_controller_mocked.balances(
        reaper_3_mock, farm_token, deployer) == 70

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 10, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 20, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 30, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 40, {'from': morpheus})
    assert farm_token.balanceOf(morpheus) == 900
    assert farm_token.balanceOf(voting_controller_mocked) == 200

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 20
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 40
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 140
    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, morpheus) == 10
    assert voting_controller_mocked.balances(
        reaper_2_mock, farm_token, morpheus) == 20
    assert voting_controller_mocked.balances(
        reaper_3_mock, farm_token, morpheus) == 70

    # initial snapshot provides equal shares between reapers
    tx = voting_controller_mocked.startVoting({'from': deployer})

    # nextSnapshotTimestamp is aligned to INIT_TIME
    assert INIT_TIME + ((chain.time() + week - INIT_TIME) // week) * week == voting_controller_mocked.nextSnapshotTimestamp()
    assert voting_controller_mocked.nextSnapshotTimestamp() == week * (voting_controller_mocked.lastSnapshotTimestamp() // week + 1)
    assert voting_controller_mocked.nextSnapshotTimestamp() - voting_controller_mocked.lastSnapshotTimestamp() <= week
    assert voting_controller_mocked.lastSnapshotTimestamp() == tx.timestamp

    init_snapshot_timestamp = voting_controller_mocked.lastSnapshotTimestamp()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 20
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 40
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 140
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_1_mock) == 0
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_2_mock) == 0
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_3_mock) == 0

    assert voting_controller_mocked.lastVotes(
        reaper_1_mock) == 333333333333333333
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 333333333333333333
    assert voting_controller_mocked.lastVotes(
        reaper_3_mock) == 333333333333333333
    assert voting_controller_mocked.lastSnapshotIndex() == 0
    init_week_number = (voting_controller_mocked.lastSnapshotTimestamp() - INIT_TIME) // week
    assert (voting_controller_mocked.nextSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    for i in range(1, 4):
        assert voting_controller_mocked.snapshots(
            voting_controller_mocked.lastSnapshotIndex(), i)[1] == 1
        assert voting_controller_mocked.snapshots(
            voting_controller_mocked.lastSnapshotIndex(), i)[2] == 333333333333333333

    exception_tester("already snapshotted", voting_controller_mocked.snapshot)

    # now current time chain.time() is ahead of voting_controller_mocked.lastSnapshotTimestamp() because of aligning
    # so wait for week - (chain.time() - voting_controller_mocked.lastSnapshotTimestamp()) + 1
    chain.mine(2, None, week - (chain.time() -
                                voting_controller_mocked.lastSnapshotTimestamp()) + 1)

    # second snapshot provides different shares between reapers
    voting_controller_mocked.snapshot()

    # nextSnapshotTimestamp is aligned to INIT_TIME
    assert INIT_TIME + ((chain.time() + week - INIT_TIME) // week) * week == voting_controller_mocked.nextSnapshotTimestamp()
    assert voting_controller_mocked.nextSnapshotTimestamp() == week * (voting_controller_mocked.lastSnapshotTimestamp() // week + 1)
    assert voting_controller_mocked.nextSnapshotTimestamp() - voting_controller_mocked.lastSnapshotTimestamp() <= week
    assert voting_controller_mocked.lastSnapshotTimestamp() + week == voting_controller_mocked.nextSnapshotTimestamp()

    second_snapshot_timestamp = voting_controller_mocked.lastSnapshotTimestamp()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 20
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 40
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 140
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_1_mock) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp)
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_2_mock) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp)
    assert voting_controller_mocked.reaperIntegratedVotes(
        reaper_3_mock) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp)
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 1 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 2 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 7 * 10 ** 17
    assert voting_controller_mocked.lastSnapshotIndex() == 1
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 1
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 20
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 40
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 140
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 1 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 2 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 7 * 10 ** 17

    # votes are changing
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 80, {'from': trinity})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 60, {'from': morpheus})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 60, {'from': deployer})
    assert farm_token.balanceOf(deployer) == initial_balance - 100 - 60
    assert farm_token.balanceOf(morpheus) == 1000 - 100 - 60
    assert farm_token.balanceOf(trinity) == 1000 - 80
    assert farm_token.balanceOf(voting_controller_mocked) == 400

    # third snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week + 1)
    voting_controller_mocked.snapshot()
    third_snapshot_timestamp = voting_controller_mocked.lastSnapshotTimestamp()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 100
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 100
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 200
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_1_mock) == 333333333333333333 * (
        second_snapshot_timestamp - init_snapshot_timestamp) + 1 * 10 ** 17 * (third_snapshot_timestamp - second_snapshot_timestamp)
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_2_mock) == 333333333333333333 * (
        second_snapshot_timestamp - init_snapshot_timestamp) + 2 * 10 ** 17 * (third_snapshot_timestamp - second_snapshot_timestamp)
    assert voting_controller_mocked.reaperIntegratedVotes(reaper_3_mock) == 333333333333333333 * (
        second_snapshot_timestamp - init_snapshot_timestamp) + 7 * 10 ** 17 * (third_snapshot_timestamp - second_snapshot_timestamp)
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 2.5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 2.5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 5 * 10 ** 17
    assert voting_controller_mocked.lastSnapshotIndex() == 2
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 2
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 100
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 100
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 200
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 2.5 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 2.5 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 5 * 10 ** 17

    # votes are changing again
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 200, {'from': trinity})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 100, {'from': morpheus})
    voting_controller_mocked.unvote(
        reaper_3_mock, farm_token, 40, {'from': deployer})
    voting_controller_mocked.vote(
        reaper_3_mock, farm_token, 140, {'from': deployer})

    # 4th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 300
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 200
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 300
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 413279999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 473759999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 927359999999999999798400
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 3.75 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 2.5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 3.75 * 10 ** 17
    assert voting_controller_mocked.lastSnapshotIndex() == 3
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 3
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 300
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 200
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 300
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 3.75 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 2.5 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 3.75 * 10 ** 17

    # votes are changing again
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 1200, {'from': deployer})

    # 5th snapshot
    assert chain.time() - voting_controller_mocked.lastSnapshotTimestamp() < 50
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week+1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 300
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 1400
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 300
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 640079999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 624959999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1154159999999999999798400
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 1.5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 7 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 1.5 * 10 ** 17
    assert voting_controller_mocked.lastSnapshotIndex() == 4
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 4
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 300
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 1400
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 300
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 1.5 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 7 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 1.5 * 10 ** 17

    # votes are changing again
    assert chain.time() - voting_controller_mocked.lastSnapshotTimestamp() < 50
    chain.mine(2, None, day + 1)

    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 300, {'from': trinity})

    assert voting_controller_mocked.balances(
        reaper_3_mock, farm_token, deployer) == 230
    assert voting_controller_mocked.balances(
        reaper_3_mock, farm_token, morpheus) == 70

    assert voting_controller_mocked.availableToUnvote(
        reaper_3_mock, farm_token, deployer, {'from': deployer}) == 230
    assert voting_controller_mocked.availableToUnvote(
        reaper_3_mock, farm_token, morpheus, {'from': deployer}) == 70
    voting_controller_mocked.unvote(
        reaper_3_mock, farm_token, 230, {'from': deployer})
    voting_controller_mocked.unvote(
        reaper_3_mock, farm_token, 70, {'from': morpheus})

    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    assert voting_controller_mocked.balances(
        reaper_3_mock, farm_token, deployer) == 0
    assert voting_controller_mocked.balances(
        reaper_3_mock, farm_token, morpheus) == 0

    # 6th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week - day + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 600
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 1400
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 730799999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 1048319999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1244879999999999999798400
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 3 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 7 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastSnapshotIndex() == 5
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 5
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 600
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 1400
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 3 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 7 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 0

    # votes are changing again
    assert chain.time() - voting_controller_mocked.lastSnapshotTimestamp() < 50
    chain.mine(2, None, day + 1)
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 400, {'from': trinity})
    voting_controller_mocked.vote(
        reaper_2_mock, farm_token, 600, {'from': morpheus})

    # 7th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week - day + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 1000
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 2000
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 912239999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 1471679999999999999798400
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1244879999999999999798400
    assert voting_controller_mocked.lastVotes(
        reaper_1_mock) == 333333333333333333
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 666666666666666666
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastSnapshotIndex() == 6
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 6
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 1000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 2000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 333333333333333333
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 666666666666666666
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 0

    # votes are not changing
    # 8th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week + 2 * day + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 1000
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 2000
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 1113839999999999999596800
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 1874879999999999999395200
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1244879999999999999798400
    assert voting_controller_mocked.lastVotes(
        reaper_1_mock) == 333333333333333333
    assert voting_controller_mocked.lastVotes(
        reaper_2_mock) == 666666666666666666
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastSnapshotIndex() == 7
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 7
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 1000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 2000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 333333333333333333
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 666666666666666666
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 0

    # votes are changing
    voting_controller_mocked.vote(
        reaper_1_mock, farm_token, 1000, {'from': thomas})
    assert farm_token.balanceOf(thomas) == 0
    assert farm_token.balanceOf(voting_controller_mocked) == 4000

    # 9th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week - 2 * day + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 2000
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 2000
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 1315439999999999999395200
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 2278079999999999998992000
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1244879999999999999798400
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 5 * 10 ** 17
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastSnapshotIndex() == 8
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 8
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 2000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 2000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 5 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 5 * 10 ** 17
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 0

    # votes are changing
    chain.mine(2, None, 2 * day + 1)
    assert voting_controller_mocked.availableToUnvote(
        reaper_1_mock, farm_token, thomas) == 1000
    voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, 1000, {'from': thomas})
    assert farm_token.balanceOf(thomas) == 1000
    assert farm_token.balanceOf(voting_controller_mocked) == 3000

    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, deployer) == 10
    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, morpheus) == 10
    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, trinity) == 980

    exception_tester("", voting_controller_mocked.unvote,
                     reaper_1_mock, farm_token, 20, {'from': deployer})
    voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, 10, {'from': deployer})
    voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, 10, {'from': morpheus})
    voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, 980, {'from': trinity})

    assert farm_token.balanceOf(morpheus) == 220
    assert farm_token.balanceOf(trinity) == 1000
    assert farm_token.balanceOf(voting_controller_mocked) == 2000

    # 10th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 0
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 2000
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 1617839999999999999395200
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 2580479999999999998992000
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1244879999999999999798400
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 0
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 10 ** 18
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastSnapshotIndex() == 9
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 9
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 2000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 10 ** 18
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 0

    # 11th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    # wait for extra time
    chain.mine(2, None, week * 2 + 1)
    voting_controller_mocked.snapshot()

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 0
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 2000
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_1_mock) == 1617839999999999999395200
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_2_mock) == 3790079999999999998992000
    # assert voting_controller_mocked.reaperIntegratedVotes(
    #     reaper_3_mock) == 1244879999999999999798400
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 0
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 10 ** 18
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
    assert voting_controller_mocked.lastSnapshotIndex() == 10
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) / week == init_week_number + 11
    assert (voting_controller_mocked.lastSnapshotTimestamp() -
            INIT_TIME) % week == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[0] == reaper_1_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[0] == reaper_2_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[0] == reaper_3_mock
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[1] == 2000
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[1] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 1)[2] == 0
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 2)[2] == 10 ** 18
    assert voting_controller_mocked.snapshots(
        voting_controller_mocked.lastSnapshotIndex(), 3)[2] == 0

    # unvote all remaining
    assert voting_controller_mocked.balances(
        reaper_2_mock, farm_token, deployer) == 1220
    assert voting_controller_mocked.balances(
        reaper_2_mock, farm_token, morpheus) == 780

    voting_controller_mocked.unvote(
        reaper_2_mock, farm_token, 1220, {'from': deployer})
    voting_controller_mocked.unvote(
        reaper_2_mock, farm_token, 780, {'from': morpheus})

    assert farm_token.balanceOf(deployer) == initial_balance
    assert farm_token.balanceOf(morpheus) == 1000
    assert farm_token.balanceOf(voting_controller_mocked) == 0

    # 12th snapshot
    exception_tester("already snapshotted", voting_controller_mocked.snapshot)
    chain.mine(2, None, week + 1)

    # total vote balance == 0, unreal in production usage
    exception_tester("Division by zero", voting_controller_mocked.snapshot)

    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 0
    assert voting_controller_mocked.reaperBalances(
        reaper_2_mock, farm_token) == 0
    assert voting_controller_mocked.reaperBalances(
        reaper_3_mock, farm_token) == 0
    assert voting_controller_mocked.lastVotes(reaper_1_mock) == 0
    assert voting_controller_mocked.lastVotes(reaper_2_mock) == 10 ** 18
    assert voting_controller_mocked.lastVotes(reaper_3_mock) == 0
