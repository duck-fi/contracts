#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


def test_transferOwnership_owner_only(voting_controller, accounts):
    with brownie.reverts("owner only"):
        voting_controller.transferOwnership(accounts[1], {'from': accounts[1]})


def test_applyOwnership_owner_only(voting_controller, accounts):
    with brownie.reverts("owner only"):
        voting_controller.applyOwnership({'from': accounts[1]})


def test_apply_without_transferOwnership(voting_controller, accounts):
    with brownie.reverts("owner not set"):
        voting_controller.applyOwnership({'from': accounts[0]})


def test_transferOwnership(voting_controller, accounts):
    voting_controller.transferOwnership(accounts[1], {'from': accounts[0]})

    assert voting_controller.owner() == accounts[0]
    assert voting_controller.futureOwner() == accounts[1]


def test_applyOwnership(voting_controller, accounts):
    voting_controller.transferOwnership(accounts[1], {'from': accounts[0]})
    voting_controller.applyOwnership({'from': accounts[0]})

    assert voting_controller.owner() == accounts[1]
    assert  voting_controller.futureOwner() == accounts[1]
