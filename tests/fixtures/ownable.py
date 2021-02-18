import pytest
import brownie


@pytest.fixture
def ownable_tester(deployer, thomas):
    def _test(contract):
        assert contract.owner() == deployer
        with brownie.reverts("owner only"):
            contract.transferOwnership(thomas, {'from': thomas})
        with brownie.reverts("owner only"):
            contract.applyOwnership({'from': thomas})
        with brownie.reverts("owner not set"):
            contract.applyOwnership({'from': deployer})

        contract.transferOwnership(thomas, {'from': deployer})
        assert contract.futureOwner() == thomas
        contract.applyOwnership({'from': deployer})
        assert contract.owner() == thomas

        contract.transferOwnership(deployer, {'from': thomas})
        contract.applyOwnership({'from': thomas})

    yield _test


@pytest.fixture
def ownable_exception_tester(exception_tester):
    def _test(fn, *args):
        exception_tester("owner only", fn, *args)

    yield _test
