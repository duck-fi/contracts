import pytest
import brownie
from brownie.test import given, strategy


@pytest.fixture
def erc20_tester(deployer, morpheus, trinity, thomas, oracle, ZERO_ADDRESS):
    @given(account=strategy('address', exclude=deployer))
    def test_balance_is_zero(contract, account):
        assert contract.balanceOf(account) == 0

    @given(account=strategy('address'))
    def test_initial_approval_is_zero(contract, account):
        assert contract.allowance(deployer, account) == 0

    @given(amount=strategy('uint256', min_value=1), another_amount=strategy('uint256', min_value=1))
    def test_modify_approve_nonzero(contract, amount, another_amount):
        tx = contract.approve(morpheus, amount, {'from': deployer})
        assert tx.return_value is True
        assert len(tx.events) == 1
        assert tx.events["Approval"].values() == [deployer, morpheus, amount]
        assert contract.allowance(deployer, morpheus) == amount
        with brownie.reverts():
            contract.approve(morpheus, another_amount, {'from': deployer})

    @given(amount=strategy('uint256', min_value=1), another_amount=strategy('uint256', min_value=1))
    def test_modify_approve_zero_nonzero(contract, amount, another_amount):
        contract.approve(morpheus, 0, {'from': deployer})
        contract.approve(morpheus, amount, {'from': deployer})
        assert contract.allowance(deployer, morpheus) == amount
        contract.approve(morpheus, 0, {'from': deployer})
        contract.approve(morpheus, another_amount, {'from': deployer})
        assert contract.allowance(deployer, morpheus) == another_amount

    @given(amount=strategy('uint256', min_value=1))
    def test_approve_self(contract, amount):
        tx = contract.approve(deployer, amount, {'from': deployer})
        assert len(tx.events) == 1
        assert tx.events["Approval"].values() == [deployer, deployer, amount]
        assert tx.return_value is True
        assert contract.allowance(deployer, deployer) == amount

    def _test(contract, name, symbol, decimals, initial_supply=0):
        # initial asserts
        assert contract.name() == name
        assert contract.symbol() == symbol
        assert contract.decimals() == decimals
        assert contract.totalSupply() == initial_supply
        assert contract.balanceOf(deployer) == contract.totalSupply()
        test_balance_is_zero(contract)

        # approve asserts
        test_initial_approval_is_zero(contract)
        contract.approve(morpheus, 10 ** 19, {'from': deployer})
        assert contract.allowance(deployer, morpheus) == 10 ** 19
        contract.approve(morpheus, 0, {'from': deployer})
        assert contract.allowance(deployer, morpheus) == 0
        test_modify_approve_nonzero(contract)
        test_modify_approve_zero_nonzero(contract)
        contract.approve(morpheus, 0, {'from': deployer})  # revoke allowance
        assert contract.allowance(deployer, morpheus) == 0
        test_approve_self(contract)
        assert contract.allowance(morpheus, deployer) == 0

        # transfer
        if contract.totalSupply():
            @given(amount=strategy('uint256', min_value=1, max_value=contract.totalSupply() / 1_000))
            def test_transfer(amount):
                total_supply = contract.totalSupply()
                sender_balance = contract.balanceOf(deployer)
                receiver_balance = contract.balanceOf(morpheus)

                tx = contract.transfer(morpheus, amount, {'from': deployer})
                assert tx.return_value is True
                assert contract.balanceOf(
                    morpheus) == receiver_balance + amount
                assert contract.balanceOf(deployer) == sender_balance - amount
                assert contract.totalSupply() == total_supply
                assert len(tx.events) == 1
                assert tx.events["Transfer"].values() == [
                    deployer, morpheus, amount]
            test_transfer()
        # transfer full balance
        amount = contract.balanceOf(deployer)
        receiver_balance = contract.balanceOf(morpheus)
        tx = contract.transfer(morpheus, amount, {'from': deployer})
        assert tx.return_value is True
        assert len(tx.events) == 1
        assert tx.events["Transfer"].values() == [deployer, morpheus, amount]
        assert contract.balanceOf(deployer) == 0
        assert contract.balanceOf(morpheus) == receiver_balance + amount
        contract.transfer(deployer, amount, {'from': morpheus})
        # transfer zero
        sender_balance = contract.balanceOf(deployer)
        receiver_balance = contract.balanceOf(morpheus)
        tx = contract.transfer(morpheus, 0, {'from': deployer})
        assert tx.return_value is True
        assert len(tx.events) == 1
        assert tx.events["Transfer"].values() == [deployer, morpheus, 0]
        assert contract.balanceOf(deployer) == sender_balance
        assert contract.balanceOf(morpheus) == receiver_balance
        # self transfer
        sender_balance = contract.balanceOf(deployer)
        contract.transfer(deployer, amount, {'from': deployer})
        assert contract.balanceOf(deployer) == sender_balance
        # insufficient balance
        with brownie.reverts():
            contract.transfer(
                morpheus, sender_balance + 1, {'from': deployer})
        # transfer to ZERO
        with brownie.reverts("recipient is zero address"):
            contract.transfer(ZERO_ADDRESS, 1, {'from': deployer})

        # transferFrom
        if contract.balanceOf(deployer):
            @given(amount=strategy('uint256', min_value=1, max_value=contract.balanceOf(deployer) / 1_000))
            def test_sender_balance_decreases(amount):
                sender_balance = contract.balanceOf(deployer)
                receiver_balance = contract.balanceOf(trinity)
                caller_balance = contract.balanceOf(morpheus)
                total_supply = contract.totalSupply()

                contract.approve(morpheus, sender_balance, {'from': deployer})
                contract.approve(trinity, sender_balance, {'from': deployer})
                tx = contract.transferFrom(
                    deployer, trinity, amount, {'from': morpheus})
                assert tx.return_value is True
                assert len(tx.events) == 1
                assert tx.events["Transfer"].values() == [
                    deployer, trinity, amount]

                assert contract.balanceOf(deployer) == sender_balance - amount
                assert contract.balanceOf(
                    trinity) == receiver_balance + amount
                assert contract.balanceOf(morpheus) == caller_balance
                assert contract.totalSupply() == total_supply
                assert contract.allowance(
                    deployer, morpheus) == sender_balance - amount
                assert contract.allowance(deployer, trinity) == sender_balance

            @given(amount=strategy('uint256', min_value=1, max_value=contract.totalSupply() / 1_000))
            def test_max_allowance(amount):
                contract.approve(morpheus, 0, {'from': deployer})
                contract.approve(morpheus, 2**256 - 1, {'from': deployer})
                contract.transferFrom(
                    deployer, trinity, amount, {'from': morpheus})
                assert contract.allowance(deployer, morpheus) == 2 ** 256 - 1

            test_sender_balance_decreases()
            test_max_allowance()
        # transferFrom zero
        sender_balance = contract.balanceOf(deployer)
        receiver_balance = contract.balanceOf(morpheus)
        contract.approve(morpheus, 0, {'from': deployer})
        contract.approve(morpheus, 10, {'from': deployer})
        contract.transferFrom(deployer, trinity, 0, {'from': morpheus})
        assert contract.balanceOf(deployer) == sender_balance
        assert contract.balanceOf(morpheus) == receiver_balance
        # without approve
        with brownie.reverts():
            contract.transferFrom(
                trinity, oracle, receiver_balance, {'from': morpheus})
        # revoke approve
        contract.approve(morpheus, 0, {'from': deployer})
        with brownie.reverts():
            contract.transferFrom(
                deployer, trinity, sender_balance, {'from': morpheus})
        # insufficient allowance
        contract.approve(morpheus, sender_balance - 1, {'from': deployer})
        with brownie.reverts():
            contract.transferFrom(
                deployer, trinity, sender_balance, {'from': morpheus})
        # to self without approve
        with brownie.reverts():
            contract.transferFrom(deployer, deployer,
                                  amount, {'from': deployer})
        # to self
        contract.approve(deployer, 0, {'from': deployer})
        contract.approve(deployer, sender_balance, {'from': deployer})
        contract.transferFrom(deployer, deployer,
                              sender_balance, {'from': deployer})
        assert contract.balanceOf(deployer) == sender_balance
        assert contract.allowance(deployer, deployer) == 0
        # insufficient balance
        contract.approve(thomas, 0, {'from': deployer})
        contract.approve(thomas, sender_balance + 1, {'from': deployer})
        with brownie.reverts():
            contract.transferFrom(
                deployer, thomas, sender_balance + 1, {'from': thomas})
        # transfer zero without approve
        sender_balance = contract.balanceOf(morpheus)
        receiver_balance = contract.balanceOf(trinity)
        contract.transferFrom(morpheus, trinity, 0, {'from': deployer})
        assert contract.balanceOf(morpheus) == sender_balance
        assert contract.balanceOf(trinity) == receiver_balance
        # transferFrom full balance
        amount = contract.balanceOf(morpheus)
        receiver_balance = contract.balanceOf(trinity)
        contract.approve(deployer, amount, {'from': morpheus})
        contract.transferFrom(morpheus, trinity, amount, {'from': deployer})
        assert contract.balanceOf(morpheus) == 0
        assert contract.balanceOf(trinity) == receiver_balance + amount
        # transferFrom to ZERO
        with brownie.reverts("recipient is zero address"):
            contract.transferFrom(deployer, ZERO_ADDRESS,
                                  1, {'from': deployer})
        # transferFrom from ZERO
        with brownie.reverts("sender is zero address"):
            contract.transferFrom(ZERO_ADDRESS, deployer,
                                  1, {'from': deployer})

    yield _test
