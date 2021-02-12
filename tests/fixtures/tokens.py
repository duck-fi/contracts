import pytest


FARM_TOKEN_NAME = "Dispersion Farm Token"
FARM_TOKEN_SYMBOL = "DFT"
FARM_TOKEN_DECIMALS = 18
FARM_TOKEN_INITIAL_SUPPLY = 100000

USDN_TOKEN_NAME = "Neutrino USD"
USDN_TOKEN_SYMBOL = "USDN"
USDN_TOKEN_DECIMALS = 18


@pytest.fixture(scope="module")
def farm_token(FarmToken, deployer):
    farm_token = FarmToken.deploy(FARM_TOKEN_NAME, FARM_TOKEN_SYMBOL, {'from': neo})
    yield farm_token


@pytest.fixture(scope="module")
def usdn_token(StakableERC20, deployer):
    yield StakableERC20.deploy(USDN_TOKEN_NAME, USDN_TOKEN_SYMBOL, USDN_TOKEN_DECIMALS, {'from': deployer})
