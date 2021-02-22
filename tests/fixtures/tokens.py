import pytest


FARM_TOKEN_NAME = "Dispersion Farm Token"
FARM_TOKEN_SYMBOL = "DSP"
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
    farm_token = FarmToken.deploy(
        FARM_TOKEN_NAME, FARM_TOKEN_SYMBOL, {'from': deployer})
    yield farm_token


@pytest.fixture(scope="module")
def usdn_token(StakableERC20, deployer):
    yield StakableERC20.deploy(USDN_TOKEN_NAME, USDN_TOKEN_SYMBOL, USDN_TOKEN_DECIMALS, {'from': deployer})


@pytest.fixture(scope="module")
def voting_token_mocked(StrictTransfableToken, voting_controller_mocked, voting_white_list, deployer):
    contract = StrictTransfableToken.deploy(
        VOTING_TOKEN_NAME, VOTING_TOKEN_SYMBOL, voting_white_list, voting_controller_mocked, {'from': deployer})
    voting_controller_mocked.setVotingToken(contract, {'from': deployer})
    yield contract


@pytest.fixture(scope="module")
def strict_transfable_token(StrictTransfableToken, white_list, deployer):
    strict_transfable_token = StrictTransfableToken.deploy(
        "Strict Transfable Token", "STT", white_list, deployer, {'from': deployer})
    yield strict_transfable_token


@ pytest.fixture(scope="module")
def chi_token(deployer, pm):
    yield (pm('forest-friends/chi@1.0.1').ChiToken).deploy({'from': deployer})
