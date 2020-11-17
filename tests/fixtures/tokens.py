import pytest


TOKEN_NAME = "Test Token"
TOKEN_SYMBOL = "TST"
TOKEN_DECIMALS = 18
TOKEN_INITIAL_SUPPLY = 100000


@pytest.fixture(scope="module")
def farming_token(FarmingToken, neo, supply_controller):
    contract = FarmingToken.deploy(
        TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_INITIAL_SUPPLY, {'from': neo})
    contract.set_supply_controller(supply_controller, {'from': neo})
    yield contract
