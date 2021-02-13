import brownie
from brownie.test import given, strategy


@given(account=strategy('address'))
def test_initial_approval_is_zero(farm_token, neo, account):
    assert farm_token.allowance(neo, account) == 0


def test_approve(farm_token, neo, morpheus):
    farm_token.approve(morpheus, 10 ** 19, {'from': neo})
    assert farm_token.allowance(neo, morpheus) == 10 ** 19
    farm_token.approve(morpheus, 0, {'from': neo})
    assert farm_token.allowance(neo, morpheus) == 0


@given(
    amount=strategy('uint256', min_value=1),
    another_amount=strategy('uint256', min_value=1),
)
def test_modify_approve_nonzero(farm_token, neo, morpheus, amount, another_amount):
    farm_token.approve(morpheus, amount, {'from': neo})
    assert farm_token.allowance(neo, morpheus) == amount
    with brownie.reverts():
        farm_token.approve(morpheus, another_amount, {'from': neo})


@given(
    amount=strategy('uint256', min_value=1),
    another_amount=strategy('uint256', min_value=1),
)
def test_modify_approve_zero_nonzero(farm_token, neo, morpheus, amount, another_amount):
    farm_token.approve(morpheus, 0, {'from': neo})
    farm_token.approve(morpheus, amount, {'from': neo})
    assert farm_token.allowance(neo, morpheus) == amount
    farm_token.approve(morpheus, 0, {'from': neo})
    farm_token.approve(morpheus, another_amount, {'from': neo})
    assert farm_token.allowance(neo, morpheus) == another_amount


def test_revoke_approve(farm_token, neo, morpheus):
    farm_token.approve(morpheus, 0, {'from': neo})
    assert farm_token.allowance(neo, morpheus) == 0


@given(amount=strategy('uint256', min_value=1))
def test_approve_self(farm_token, neo, amount):
    farm_token.approve(neo, amount, {'from': neo})
    assert farm_token.allowance(neo, neo) == amount


def test_only_affects_target(farm_token, neo, morpheus):
    assert farm_token.allowance(morpheus, neo) == 0


@given(amount=strategy('uint256', min_value=1))
def test_returns_true(farm_token, neo, trinity, amount):
    tx = farm_token.approve(trinity, amount, {'from': neo})
    assert tx.return_value is True


@given(amount=strategy('uint256', min_value=1))
def test_approval_event_fires(farm_token, neo, morpheus, amount):
    tx = farm_token.approve(morpheus, amount, {'from': neo})

    assert len(tx.events) == 1
    assert tx.events["Approval"].values() == [neo, morpheus, amount]
