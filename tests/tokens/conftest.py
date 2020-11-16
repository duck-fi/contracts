#!/usr/bin/python3


import pytest


@pytest.fixture(scope="module")
def token(DispersionToken, neo, supply_controller):
    contract = DispersionToken.deploy(
        "Test Token", "TST", 18, 100000, {'from': neo})
    contract.set_supply_controller(supply_controller, {'from': neo})
    yield contract


@pytest.fixture(scope="module")
def supply_controller(accounts):
    yield accounts[-1]
