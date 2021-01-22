#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


WEEK = 604800


def test_voting_period_owner_only(voting_controller, accounts):
    with brownie.reverts("unauthorized"):
        voting_controller.setVotingPeriod(WEEK, {'from': accounts[1]})


def test_voting_period_set_zero(voting_controller, accounts):
    with brownie.reverts("invalid params"):
        voting_controller.setVotingPeriod(0, {'from': accounts[0]})


def test_voting_period(voting_controller, accounts):
    voting_controller.setVotingPeriod(3 * WEEK, {'from': accounts[0]})
    assert voting_controller.voting_period() == 3 * WEEK

    voting_controller.setVotingPeriod(WEEK, {'from': accounts[0]})
    assert voting_controller.voting_period() == WEEK
