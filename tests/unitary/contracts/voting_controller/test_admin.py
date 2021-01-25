#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


def test_set_admin_owner_only(voting_controller, neo, trinity):
    with brownie.reverts("unauthorized"):
        voting_controller.setAdmin(trinity, {'from': trinity})


def test_set_admin(voting_controller, neo, trinity):
    voting_controller.setAdmin(trinity, {'from': neo})
    assert voting_controller.admin() == trinity


def test_snapshot_admin_only(voting_controller, neo, trinity):
    with brownie.reverts("unauthorized"):
        voting_controller.snapshot({'from': neo})

    voting_controller.snapshot({'from': trinity})
