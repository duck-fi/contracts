import pytest


FARM_TOKEN_NAME = "Dispersion Farm Token"
FARM_TOKEN_SYMBOL = "DFT"
FARM_TOKEN_DECIMALS = 18

USDN_TOKEN_NAME = "Neutrino USD"
USDN_TOKEN_SYMBOL = "USDN"
USDN_TOKEN_DECIMALS = 18

VOTING_TOKEN_NAME = "Dispersion Voting Token"
VOTING_TOKEN_SYMBOL = "DVT"
VOTING_TOKEN_DECIMALS = 18
VOTING_TOKEN_INITIAL_SUPPLY = 1000000 * 10 ** VOTING_TOKEN_DECIMALS


@pytest.fixture(scope="module")
def farm_token(FarmToken, deployer):
    farm_token = FarmToken.deploy(FARM_TOKEN_NAME, FARM_TOKEN_SYMBOL, {'from': deployer})
    yield farm_token


@pytest.fixture(scope="module")
def usdn_token(StakableERC20, deployer):
    yield StakableERC20.deploy(USDN_TOKEN_NAME, USDN_TOKEN_SYMBOL, USDN_TOKEN_DECIMALS, {'from': deployer})


@pytest.fixture(scope="module")
def voting_token(ERC20Basic, deployer):
    voting_token = ERC20Basic.deploy(VOTING_TOKEN_NAME, VOTING_TOKEN_SYMBOL, VOTING_TOKEN_DECIMALS, VOTING_TOKEN_INITIAL_SUPPLY, {'from': deployer})
    yield voting_token
