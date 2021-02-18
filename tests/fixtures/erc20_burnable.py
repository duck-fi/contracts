from math import floor
import pytest
import brownie
from brownie.test import given, strategy


@pytest.fixture
def erc20_burnable_tester(deployer, thomas, ZERO_ADDRESS):
    def _test(contract):
        if contract.balanceOf(deployer):
            @given(amount=strategy('uint256', min_value=2, max_value=contract.balanceOf(deployer) / 1_000))
            def test_burn_affects_balance(amount):
                total_supply = contract.totalSupply()
                balance = contract.balanceOf(deployer)

                tx = contract.burn(amount, {'from': deployer})
                assert contract.balanceOf(deployer) == balance - amount
                assert contract.totalSupply() == total_supply - amount
                assert len(tx.events) == 1
                assert tx.events["Transfer"].values() == [
                    deployer, ZERO_ADDRESS, amount]

                burnAmount = floor(amount / 2)
                contract.burn(burnAmount, {'from': deployer})
                assert contract.balanceOf(
                    deployer) == balance - amount - burnAmount
                assert contract.totalSupply() == total_supply - amount - burnAmount
            test_burn_affects_balance()
        # underflow
        with brownie.reverts():
            contract.burn(contract.balanceOf(deployer) + 1, {'from': deployer})
        # burn zero
        balance = contract.balanceOf(deployer)
        contract.burn(0, {'from': deployer})
        assert balance == contract.balanceOf(deployer)
        # success burn
        balance = contract.balanceOf(deployer)
        contract.burn(balance, {'from': deployer})
        assert contract.balanceOf(deployer) == 0

    yield _test
