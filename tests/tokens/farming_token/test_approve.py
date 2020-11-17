#!/usr/bin/python3

import brownie
import pytest
from brownie.test import given, strategy


@given(account=strategy('address'))
def test_initial_approval_is_zero(farming_token, neo, account):
    assert farming_token.allowance(neo, account) == 0


def test_approve(farming_token, neo, morpheus):
    farming_token.approve(morpheus, 10 ** 19, {'from': neo})
    assert farming_token.allowance(neo, morpheus) == 10 ** 19


@given(amount=strategy('uint256', min_value=1))
def test_modify_approve_nonzero(farming_token, neo, morpheus, amount):
    with brownie.reverts():
        farming_token.approve(morpheus, amount, {'from': neo})


@given(amount=strategy('uint256', min_value=1))
def test_modify_approve_zero_nonzero(farming_token, neo, morpheus, amount):
    farming_token.approve(morpheus, 0, {'from': neo})
    farming_token.approve(morpheus, amount, {'from': neo})
    assert farming_token.allowance(neo, morpheus) == amount


def test_revoke_approve(farming_token, neo, morpheus):
    farming_token.approve(morpheus, 0, {'from': neo})
    assert farming_token.allowance(neo, morpheus) == 0


@given(amount=strategy('uint256', min_value=1))
def test_approve_self(farming_token, neo, amount):
    farming_token.approve(neo, amount, {'from': neo})
    assert farming_token.allowance(neo, neo) == amount


def test_only_affects_target(farming_token, neo, morpheus):
    assert farming_token.allowance(morpheus, neo) == 0


@given(amount=strategy('uint256', min_value=1))
def test_returns_true(farming_token, neo, trinity, amount):
    tx = farming_token.approve(trinity, amount, {'from': neo})
    assert tx.return_value is True


@given(amount=strategy('uint256', min_value=1))
def test_approval_event_fires(farming_token, neo, morpheus, amount):
    tx = farming_token.approve(morpheus, amount, {'from': neo})

    assert len(tx.events) == 1
    assert tx.events["Approval"].values() == [neo, morpheus, amount]
