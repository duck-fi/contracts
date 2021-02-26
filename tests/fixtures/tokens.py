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
VOTING_TOKEN_INITIAL_SUPPLY = 1_000_000 * 10 ** VOTING_TOKEN_DECIMALS

BOOSTING_TOKEN_NAME = "Dispersion Boosting Token"
BOOSTING_TOKEN_SYMBOL = "DBT"
BOOSTING_TOKEN_DECIMALS = 18
BOOSTING_TOKEN_INITIAL_SUPPLY = 1_000_000 * 10 ** BOOSTING_TOKEN_DECIMALS

LP_TOKEN_NAME = "LP Token"
LP_TOKEN_SYMBOL = "LPT"
LP_TOKEN_DECIMALS = 18
LP_TOKEN_INITIAL_SUPPLY = 1_000_000 * 10 ** LP_TOKEN_DECIMALS


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
def boosting_token_mocked(StrictTransfableToken, boosting_controller_mocked, boosting_white_list, deployer):
    contract = StrictTransfableToken.deploy(BOOSTING_TOKEN_NAME, BOOSTING_TOKEN_SYMBOL,
                                            boosting_white_list, boosting_controller_mocked, {'from': deployer})
    boosting_controller_mocked.setBoostingToken(contract, {'from': deployer})
    yield contract


@pytest.fixture(scope="module")
def strict_transfable_token(StrictTransfableToken, white_list, deployer):
    strict_transfable_token = StrictTransfableToken.deploy(
        "Strict Transfable Token", "STT", white_list, deployer, {'from': deployer})
    yield strict_transfable_token


@pytest.fixture(scope="module")
def chi_token(deployer, pm):
    yield (pm('forest-friends/chi@1.0.1').ChiToken).deploy({'from': deployer})


@pytest.fixture(scope="module")
def lp_token(ERC20Basic, deployer):
    yield ERC20Basic.deploy(LP_TOKEN_NAME, LP_TOKEN_SYMBOL, LP_TOKEN_DECIMALS, LP_TOKEN_INITIAL_SUPPLY, {'from': deployer})
