#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


INIT_TIME = 1609372800
DAY = 86400
WEEK = DAY * 7


def test_snapshot_1(voting_controller, farm_token, voting_strategy_stub, three_reapers_stub, neo, morpheus, trinity, thomas):
    voting_controller.setStrategy(farm_token, voting_strategy_stub, {'from': neo})
    
    farm_token.transfer(morpheus, 1000, {'from': neo})
    farm_token.transfer(trinity, 1000, {'from': neo})
    farm_token.transfer(thomas, 1000, {'from': neo})
    initial_balance = farm_token.balanceOf(neo)

    farm_token.approve(voting_controller, 2000, {'from': neo})
    farm_token.approve(voting_controller, 2000, {'from': morpheus})
    farm_token.approve(voting_controller, 2000, {'from': trinity})
    farm_token.approve(voting_controller, 2000, {'from': thomas})

    voting_controller.vote(three_reapers_stub[0], farm_token, 10, {'from': neo})
    voting_controller.vote(three_reapers_stub[1], farm_token, 20, {'from': neo})
    voting_controller.vote(three_reapers_stub[2], farm_token, 30, {'from': neo})
    voting_controller.vote(three_reapers_stub[2], farm_token, 40, {'from': neo})
    assert farm_token.balanceOf(neo) == initial_balance - 100
    assert farm_token.balanceOf(voting_controller) == 100

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 10
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 20
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 70
    assert voting_controller.balances(three_reapers_stub[0], farm_token, neo) == 10
    assert voting_controller.balances(three_reapers_stub[1], farm_token, neo) == 20
    assert voting_controller.balances(three_reapers_stub[2], farm_token, neo) == 70

    voting_controller.vote(three_reapers_stub[0], farm_token, 10, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[1], farm_token, 20, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[2], farm_token, 30, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[2], farm_token, 40, {'from': morpheus})
    assert farm_token.balanceOf(morpheus) == 900
    assert farm_token.balanceOf(voting_controller) == 200

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 20
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 40
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 140
    assert voting_controller.balances(three_reapers_stub[0], farm_token, morpheus) == 10
    assert voting_controller.balances(three_reapers_stub[1], farm_token, morpheus) == 20
    assert voting_controller.balances(three_reapers_stub[2], farm_token, morpheus) == 70

    # initial snapshot provides equal shares between reapers
    voting_controller.snapshot()
    init_snapshot_timestamp = voting_controller.last_snapshot_timestamp()
   
    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 20
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 40
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 140
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 0

    assert voting_controller.current_votes(three_reapers_stub[0]) == 333333333333333333
    assert voting_controller.current_votes(three_reapers_stub[1]) == 333333333333333333
    assert voting_controller.current_votes(three_reapers_stub[2]) == 333333333333333333
    assert voting_controller.last_snapshot_index() == 0
    init_week_number = (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[1] == 1
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[2] == 333333333333333333

    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    # now current time brownie.chain.time() is ahead of voting_controller.last_snapshot_timestamp() because of aligning
    # so wait for WEEK - (brownie.chain.time() - voting_controller.last_snapshot_timestamp()) + 1
    brownie.chain.sleep(WEEK - (brownie.chain.time() - voting_controller.last_snapshot_timestamp()) + 1)

    # second snapshot provides different shares between reapers
    voting_controller.snapshot()
    second_snapshot_timestamp = voting_controller.last_snapshot_timestamp()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 20
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 40
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 140
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp)
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp)
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp)
    assert voting_controller.current_votes(three_reapers_stub[0]) == 1 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[1]) == 2 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[2]) == 7 * 10 ** 17
    assert voting_controller.last_snapshot_index() == 1
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 1
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 20
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 40
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 140
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 1 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 2 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 7 * 10 ** 17

    # votes are changing
    voting_controller.vote(three_reapers_stub[0], farm_token, 80, {'from': trinity})
    voting_controller.vote(three_reapers_stub[1], farm_token, 60, {'from': morpheus})
    voting_controller.vote(three_reapers_stub[2], farm_token, 60, {'from': neo})
    assert farm_token.balanceOf(neo) == initial_balance - 100 - 60
    assert farm_token.balanceOf(morpheus) == 1000 - 100 - 60
    assert farm_token.balanceOf(trinity) == 1000 - 80
    assert farm_token.balanceOf(voting_controller) == 400

    # third snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK)

    voting_controller.snapshot()
    third_snapshot_timestamp = voting_controller.last_snapshot_timestamp()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 100
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 100
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 200
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp) + 1 * 10 ** 17 * (third_snapshot_timestamp - second_snapshot_timestamp)
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp) + 2 * 10 ** 17 * (third_snapshot_timestamp - second_snapshot_timestamp)
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 333333333333333333 * (second_snapshot_timestamp - init_snapshot_timestamp) + 7 * 10 ** 17 * (third_snapshot_timestamp - second_snapshot_timestamp)
    assert voting_controller.current_votes(three_reapers_stub[0]) == 2.5 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[2]) == 5 * 10 ** 17
    assert voting_controller.last_snapshot_index() == 2
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 2
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 100
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 100
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 200
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 2.5 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 2.5 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 5 * 10 ** 17

    # votes are changing again
    voting_controller.vote(three_reapers_stub[0], farm_token, 200, {'from': trinity})
    voting_controller.vote(three_reapers_stub[1], farm_token, 100, {'from': morpheus})
    voting_controller.unvote(three_reapers_stub[2], farm_token, 40, {'from': neo})
    voting_controller.vote(three_reapers_stub[2], farm_token, 140, {'from': neo})

    # 4th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 300
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 200
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 300
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 413279999999999999798400 # here and later integrals were calculated via https://www.wolframalpha.com/
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 473759999999999999798400 # here and later integrals were calculated via https://www.wolframalpha.com/
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 927359999999999999798400 # here and later integrals were calculated via https://www.wolframalpha.com/
    assert voting_controller.current_votes(three_reapers_stub[0]) == 3.75 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[1]) == 2.5 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[2]) == 3.75 * 10 ** 17
    assert voting_controller.last_snapshot_index() == 3
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 3
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 300
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 200
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 300
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 3.75 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 2.5 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 3.75 * 10 ** 17

    # votes are changing again
    voting_controller.vote(three_reapers_stub[1], farm_token, 1200, {'from': neo})

    # 5th snapshot
    assert brownie.chain.time() - voting_controller.last_snapshot_timestamp() < 10
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 300
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 1400
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 300
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 640079999999999999798400
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 624959999999999999798400
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1154159999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 1.5 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[1]) == 7 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[2]) == 1.5 * 10 ** 17
    assert voting_controller.last_snapshot_index() == 4
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 4
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 300
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 1400
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 300
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 1.5 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 7 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 1.5 * 10 ** 17

    # votes are changing again
    assert brownie.chain.time() - voting_controller.last_snapshot_timestamp() < 10
    brownie.chain.sleep(DAY)

    voting_controller.vote(three_reapers_stub[0], farm_token, 300, {'from': trinity})
    
    assert voting_controller.balances(three_reapers_stub[2], farm_token, neo) == 230
    assert voting_controller.balances(three_reapers_stub[2], farm_token, morpheus) == 70

    assert voting_controller.availableToUnvote(three_reapers_stub[2], farm_token, neo, {'from': neo}) == 230
    assert voting_controller.availableToUnvote(three_reapers_stub[2], farm_token, morpheus, {'from': neo}) == 70
    voting_controller.unvote(three_reapers_stub[2], farm_token, 230, {'from': neo})
    voting_controller.unvote(three_reapers_stub[2], farm_token, 70, {'from': morpheus})

    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.balances(three_reapers_stub[2], farm_token, neo) == 0
    assert voting_controller.balances(three_reapers_stub[2], farm_token, morpheus) == 0

    # 6th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK - DAY)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 600
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 1400
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 730799999999999999798400
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 1048319999999999999798400
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1244879999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 3 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[1]) == 7 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
    assert voting_controller.last_snapshot_index() == 5
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 5
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 600
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 1400
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 3 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 7 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 0

    # votes are changing again
    assert brownie.chain.time() - voting_controller.last_snapshot_timestamp() < 10
    brownie.chain.sleep(DAY)
    voting_controller.vote(three_reapers_stub[0], farm_token, 400, {'from': trinity})
    voting_controller.vote(three_reapers_stub[1], farm_token, 600, {'from': morpheus})

    # 7th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK-DAY)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 1000
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 2000
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 912239999999999999798400
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 1471679999999999999798400
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1244879999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 333333333333333333
    assert voting_controller.current_votes(three_reapers_stub[1]) == 666666666666666666
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
    assert voting_controller.last_snapshot_index() == 6
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 6
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 1000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 2000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 333333333333333333
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 666666666666666666
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 0

    # votes are not changing
    # 8th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK+2*DAY)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 1000
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 2000
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 1113839999999999999596800
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 1874879999999999999395200
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1244879999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 333333333333333333
    assert voting_controller.current_votes(three_reapers_stub[1]) == 666666666666666666
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
    assert voting_controller.last_snapshot_index() == 7
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 7
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 1000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 2000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 333333333333333333
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 666666666666666666
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 0

    # votes are changing
    voting_controller.vote(three_reapers_stub[0], farm_token, 1000, {'from': thomas})
    assert farm_token.balanceOf(thomas) == 0
    assert farm_token.balanceOf(voting_controller) == 4000

    # 9th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK-2*DAY)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 2000
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 2000
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 1315439999999999999395200
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 2278079999999999998992000
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1244879999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 5 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[1]) == 5 * 10 ** 17
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
    assert voting_controller.last_snapshot_index() == 8
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 8
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 2000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 2000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 5 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 5 * 10 ** 17
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 0

    # votes are changing
    assert voting_controller.availableToUnvote(three_reapers_stub[0], farm_token, thomas) == 1000
    voting_controller.unvote(three_reapers_stub[0], farm_token, 1000, {'from': thomas})
    assert farm_token.balanceOf(thomas) == 1000
    assert farm_token.balanceOf(voting_controller) == 3000

    assert voting_controller.balances(three_reapers_stub[0], farm_token, neo) == 10
    assert voting_controller.balances(three_reapers_stub[0], farm_token, morpheus) == 10
    assert voting_controller.balances(three_reapers_stub[0], farm_token, trinity) == 980
    
    with brownie.reverts():
        voting_controller.unvote(three_reapers_stub[0], farm_token, 20, {'from': neo})
    voting_controller.unvote(three_reapers_stub[0], farm_token, 10, {'from': neo})
    voting_controller.unvote(three_reapers_stub[0], farm_token, 10, {'from': morpheus})
    voting_controller.unvote(three_reapers_stub[0], farm_token, 980, {'from': trinity})

    assert farm_token.balanceOf(morpheus) == 220
    assert farm_token.balanceOf(trinity) == 1000
    assert farm_token.balanceOf(voting_controller) == 2000

    # 10th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()

    brownie.chain.sleep(WEEK)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 0
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 2000
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 1617839999999999999395200
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 2580479999999999998992000
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1244879999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 0
    assert voting_controller.current_votes(three_reapers_stub[1]) == 10 ** 18
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
    assert voting_controller.last_snapshot_index() == 9
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 9
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 2000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 10 ** 18
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 0

    # 11th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()
    
    # wait for extra time
    brownie.chain.sleep(WEEK*2)
    voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 0
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 2000
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[0]) == 1617839999999999999395200
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[1]) == 3790079999999999998992000
    assert voting_controller.reaper_integrated_votes(three_reapers_stub[2]) == 1244879999999999999798400
    assert voting_controller.current_votes(three_reapers_stub[0]) == 0
    assert voting_controller.current_votes(three_reapers_stub[1]) == 10 ** 18
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
    assert voting_controller.last_snapshot_index() == 10
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) / WEEK == init_week_number + 11
    assert (voting_controller.last_snapshot_timestamp() - INIT_TIME) % WEEK == 0
    for i in range(1, 4):
        assert voting_controller.snapshots(voting_controller.last_snapshot_index(), i)[0] == three_reapers_stub[i - 1]
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[1] == 2000
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[1] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 1)[2] == 0
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 2)[2] == 10 ** 18
    assert voting_controller.snapshots(voting_controller.last_snapshot_index(), 3)[2] == 0

    # unvote all remaining
    assert voting_controller.balances(three_reapers_stub[1], farm_token, neo) == 1220
    assert voting_controller.balances(three_reapers_stub[1], farm_token, morpheus) == 780
    
    voting_controller.unvote(three_reapers_stub[1], farm_token, 1220, {'from': neo})
    voting_controller.unvote(three_reapers_stub[1], farm_token, 780, {'from': morpheus})

    assert farm_token.balanceOf(neo) == initial_balance
    assert farm_token.balanceOf(morpheus) == 1000
    assert farm_token.balanceOf(voting_controller) == 0

    # 12th snapshot
    with brownie.reverts("already snapshotted"):
        voting_controller.snapshot()
    
    brownie.chain.sleep(WEEK)

    with brownie.reverts("Division by zero"): # total vote balance == 0, unreal in production usage
        voting_controller.snapshot()

    assert voting_controller.reaper_balances(three_reapers_stub[0], farm_token) == 0
    assert voting_controller.reaper_balances(three_reapers_stub[1], farm_token) == 0
    assert voting_controller.reaper_balances(three_reapers_stub[2], farm_token) == 0
    assert voting_controller.current_votes(three_reapers_stub[0]) == 0
    assert voting_controller.current_votes(three_reapers_stub[1]) == 10 ** 18
    assert voting_controller.current_votes(three_reapers_stub[2]) == 0
