#!/usr/bin/python3


import brownie
import pytest
from brownie.test import given, strategy


@pytest.mark.parametrize("idx", range(5))
def test_initial_approval_is_zero(token, neo, accounts, idx):
    assert token.allowance(neo, accounts[idx]) == 0


def test_approve(token, neo, morpheus):
    token.approve(morpheus, 10 ** 19, {'from': neo})
    assert token.allowance(neo, morpheus) == 10 ** 19


@given(amount=strategy('uint256', min_value=1))
def test_modify_approve_nonzero(token, neo, morpheus, amount):
    with brownie.reverts():
        token.approve(morpheus, amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_modify_approve_zero_nonzero(token, neo, morpheus, amount):
    token.approve(morpheus, 0, {'from': neo})
    token.approve(morpheus, amount, {'from': neo})
    assert token.allowance(neo, morpheus) == amount


def test_revoke_approve(token, neo, morpheus):
    token.approve(morpheus, 0, {'from': neo})
    assert token.allowance(neo, morpheus) == 0


@given(amount=strategy('uint256', min_value=1))
def test_approve_self(token, neo, amount):
    token.approve(neo, amount, {'from': neo})
    assert token.allowance(neo, neo) == amount


def test_only_affects_target(token, neo, morpheus):
    assert token.allowance(morpheus, neo) == 0


@given(amount=strategy('uint256', min_value=1))
def test_returns_true(token, neo, trinity, amount):
    tx = token.approve(trinity, amount, {'from': neo})
    assert tx.return_value is True


@given(amount=strategy('uint256', min_value=1))
def test_approval_event_fires(neo, morpheus, token, amount):
    tx = token.approve(morpheus, amount, {'from': neo})

    assert len(tx.events) == 1
    assert tx.events["Approval"].values() == [neo, morpheus, amount]
