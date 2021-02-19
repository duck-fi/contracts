from brownie.test import given, strategy


def test_unsupported_reaper(voting_controller_mocked, exception_tester, thomas, deployer, farm_token):
    exception_tester("invalid reaper", voting_controller_mocked.vote,
                     thomas, farm_token, 1, {'from': deployer})


def test_zero_reaper(voting_controller_mocked, exception_tester, ZERO_ADDRESS, deployer, farm_token):
    exception_tester("invalid reaper", voting_controller_mocked.vote,
                     ZERO_ADDRESS, farm_token, 1, {'from': deployer})


def test_unsupported_coin(voting_controller_mocked, reaper_1_mock, exception_tester, deployer, thomas):
    exception_tester("invalid coin", voting_controller_mocked.vote,
                     reaper_1_mock, thomas, 1, {'from': deployer})


def test_unsupported_coin(voting_controller_mocked, reaper_1_mock, exception_tester, deployer, ZERO_ADDRESS):
    exception_tester("invalid coin", voting_controller_mocked.vote,
                     reaper_1_mock, ZERO_ADDRESS, 1, {'from': deployer})


def test_unapproved(voting_controller_mocked, reaper_1_mock, exception_tester, farm_token, morpheus):
    exception_tester("", voting_controller_mocked.vote,
                     reaper_1_mock, farm_token, 1, {'from': morpheus})


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_vote_simple(exception_tester, voting_controller_mocked, farm_token, reaper_1_mock, deployer, amount, week, chain):
    initial_balance = farm_token.balanceOf(deployer)
    farm_token.approve(voting_controller_mocked, amount, {'from': deployer})
    tx1 = voting_controller_mocked.vote(
        reaper_1_mock, farm_token, amount, {'from': deployer})
    assert tx1.return_value is None
    assert len(tx1.events) == 2
    assert tx1.events["Transfer"].values(
    ) == [deployer, voting_controller_mocked, amount]
    assert tx1.events["Vote"].values(
    ) == [reaper_1_mock, farm_token, deployer, amount]

    exception_tester("", voting_controller_mocked.vote,
                     reaper_1_mock, farm_token, amount, {'from': deployer})

    assert farm_token.balanceOf(deployer) == initial_balance - amount
    assert farm_token.balanceOf(voting_controller_mocked) == amount
    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == amount
    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, deployer) == amount
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, deployer) == amount
    assert voting_controller_mocked.availableToUnvote(
        reaper_1_mock, farm_token, deployer) == 0

    exception_tester("tokens are locked", voting_controller_mocked.unvote,
                     reaper_1_mock, farm_token, amount, {'from': deployer})

    chain.mine(1, chain.time() + week + 1)
    assert voting_controller_mocked.availableToUnvote(
        reaper_1_mock, farm_token, deployer) == amount

    tx2 = voting_controller_mocked.unvote(
        reaper_1_mock, farm_token, amount, {'from': deployer})

    assert tx2.return_value is None
    assert len(tx2.events) == 2
    assert tx2.events["Transfer"].values(
    ) == [voting_controller_mocked, deployer, amount]
    assert tx2.events["Unvote"].values(
    ) == [reaper_1_mock, farm_token, deployer, amount]

    assert farm_token.balanceOf(deployer) == initial_balance
    assert farm_token.balanceOf(voting_controller_mocked) == 0
    assert voting_controller_mocked.reaperBalances(
        reaper_1_mock, farm_token) == 0
    assert voting_controller_mocked.balances(
        reaper_1_mock, farm_token, deployer) == 0
    assert voting_controller_mocked.accountVotePower(
        reaper_1_mock, deployer) == 0
    assert voting_controller_mocked.availableToUnvote(
        reaper_1_mock, farm_token, deployer) == 0


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_vote_gas_reducing(voting_controller_mocked, farm_token, reaper_1_mock, trinity, deployer, amount, chi_token, chain):
    chi_token.mint(10, {'from': trinity})
    chi_token.approve(voting_controller_mocked, 10, {'from': trinity})
    chain.mine(1, chain.time() + 1)
    farm_token.transfer(trinity, 1_000, {'from': deployer})
    farm_token.approve(voting_controller_mocked, amount, {'from': deployer})
    farm_token.approve(voting_controller_mocked, amount, {'from': trinity})

    tx1 = voting_controller_mocked.vote(
        reaper_1_mock, farm_token, amount, {'from': deployer})
    tx2 = voting_controller_mocked.vote(
        reaper_1_mock, farm_token, amount, chi_token, {'from': trinity})
    assert tx1.return_value is None
    assert tx2.return_value is None
    assert len(tx1.events) == 2
    assert len(tx2.events) == 4
    assert tx1.events["Transfer"].values(
    ) == [deployer, voting_controller_mocked, amount]
    assert tx2.events["Transfer"].values(
    ) == [trinity, voting_controller_mocked, amount]
    assert tx1.events["Vote"].values(
    ) == [reaper_1_mock, farm_token, deployer, amount]
    assert tx2.events["Vote"].values(
    ) == [reaper_1_mock, farm_token, trinity, amount]

    assert 10 - chi_token.balanceOf(trinity) == 2


@given(amount=strategy('uint256', min_value=1, max_value=1_000))
def test_vote_gas_reducing_not_valid_token(voting_controller_mocked, farm_token, reaper_1_mock, exception_tester, deployer, amount):
    farm_token.approve(voting_controller_mocked, amount, {'from': deployer})
    exception_tester("unsupported gas token", voting_controller_mocked.vote,
                     reaper_1_mock, farm_token, amount, farm_token, {'from': deployer})
