import pytest


FARM_TOKEN_NAME = "Dispersion Farm Token"
FARM_TOKEN_SYMBOL = "DSP"
FARM_TOKEN_DECIMALS = 18

USDN_TOKEN_NAME = "Neutrino USD"
USDN_TOKEN_SYMBOL = "USDN"
USDN_TOKEN_DECIMALS = 18

WAVES_TOKEN_NAME = "Waves"
WAVES_TOKEN_SYMBOL = "WAVES"
WAVES_TOKEN_DECIMALS = 18

LP_TOKEN_NAME = "LP Token"
LP_TOKEN_SYMBOL = "LPT"
LP_TOKEN_DECIMALS = 18
LP_TOKEN_INITIAL_SUPPLY = 1000000 * 10 ** LP_TOKEN_DECIMALS

CRV_TOKEN_NAME = "CRV Token"
CRV_TOKEN_SYMBOL = "CRV"
CRV_TOKEN_DECIMALS = 18
CRV_TOKEN_INITIAL_SUPPLY = 1000000 * 10 ** LP_TOKEN_DECIMALS

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
def waves_token(StakableERC20, deployer):
    yield StakableERC20.deploy(USDN_TOKEN_NAME, USDN_TOKEN_SYMBOL, USDN_TOKEN_DECIMALS, {'from': deployer})


@pytest.fixture(scope="module")
def lp_token(ERC20Basic, deployer):
    yield ERC20Basic.deploy(LP_TOKEN_NAME, LP_TOKEN_SYMBOL, LP_TOKEN_DECIMALS, LP_TOKEN_INITIAL_SUPPLY, {'from': deployer})


@pytest.fixture(scope="module")
def crv_token_mock(ERC20Basic, deployer):
    yield ERC20Basic.deploy(CRV_TOKEN_NAME, CRV_TOKEN_SYMBOL, CRV_TOKEN_DECIMALS, CRV_TOKEN_INITIAL_SUPPLY, {'from': deployer})


@pytest.fixture(scope="module")
def voting_token_mocked(StrictTransferableToken, voting_controller_mocked, voting_white_list, WhiteList, deployer):
    voting_transferable_white_list = WhiteList.deploy({'from': deployer})
    voting_transferable_white_list.addAddress(voting_controller_mocked, {'from': deployer})
    contract = StrictTransferableToken.deploy(
        VOTING_TOKEN_NAME, VOTING_TOKEN_SYMBOL, voting_white_list, voting_transferable_white_list, {'from': deployer})
    voting_controller_mocked.setVotingToken(contract, {'from': deployer})
    yield contract


@pytest.fixture(scope="module")
def boosting_token_mocked(StrictTransferableToken, boosting_controller_mocked, boosting_white_list, WhiteList, deployer):
    boosting_transferable_white_list = WhiteList.deploy({'from': deployer})
    boosting_transferable_white_list.addAddress(boosting_controller_mocked, {'from': deployer})
    contract = StrictTransferableToken.deploy(BOOSTING_TOKEN_NAME, BOOSTING_TOKEN_SYMBOL,
                                            boosting_white_list, boosting_transferable_white_list, {'from': deployer})
    boosting_controller_mocked.setBoostingToken(contract, {'from': deployer})
    yield contract


@pytest.fixture(scope="module")
def strict_transferable_token(StrictTransferableToken, white_list, deployer):
    strict_transferable_token = StrictTransferableToken.deploy(
        "Strict Transferable Token", "STT", white_list, white_list, {'from': deployer})
    yield strict_transferable_token


@pytest.fixture(scope="module")
def chi_token(deployer, pm):
    yield (pm('forest-friends/chi@1.0.1').ChiToken).deploy({'from': deployer})
