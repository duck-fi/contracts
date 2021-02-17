import brownie
from brownie.test import given, strategy

# TODO consider to move into shared place/module


def to_raw_farm_token(dec_amount: float) -> int:
    return dec_amount * (10 ** FARM_TOKEN_DECIMALS)


def to_dec_farm_token(raw_amount: int) -> float:
    return raw_amount / (10 ** FARM_TOKEN_DECIMALS)


FARM_TOKEN_DECIMALS = 18
FARM_TOKEN_INITIAL_SUPPLY_DEC = 100_000
INITIAL_EMISSION_DEC = 1_000_000
INITIAL_EMISSION_RAW = to_raw_farm_token(INITIAL_EMISSION_DEC)
SECONDS_IN_YEAR = 86_400 * 365
EMISSION_REDUCTION_SECONDS = SECONDS_IN_YEAR


def test_fail_to_update_minter_not_by_owner(farm_token, ownable_exception_tester, thomas, morpheus):
    ownable_exception_tester(farm_token.setMinter, morpheus, {'from': thomas})


def test_fail_to_startEmission_not_by_owner(farm_token, thomas, ownable_exception_tester):
    ownable_exception_tester(farm_token.startEmission, {'from': thomas})


def test_mint_not_minter(farm_token, thomas, exception_tester):
    exception_tester("minter only", farm_token.mint,
                     thomas, 1, {'from': thomas})


def test_success_update_minter_by_owner(farm_token, deployer, morpheus):
    farm_token.setMinter(morpheus, {'from': deployer})
    farm_token.setMinter(deployer, {'from': deployer})


def test_transferFrom_without_approval_by_minter(farm_token, deployer, morpheus):
    balance = farm_token.balanceOf(deployer)
    amount = balance / 2
    farm_token.transfer(morpheus, amount, {'from': deployer})

    assert farm_token.balanceOf(deployer) == balance - amount
    assert farm_token.balanceOf(morpheus) == amount


@ given(amount=strategy('uint256', min_value=1))
def test_fail_to_mint_beforeStartEmission(farm_token, deployer, trinity, amount):
    with brownie.reverts("exceeds allowable mint amount"):
        farm_token.mint(trinity, amount, {'from': deployer})


def assert_emission(farm_token, expected_yearEmission):
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()
    assert farm_token.yearEmission(
    ).return_value == expected_yearEmission, "invalid yearEmission"
    missionIntegralTx = farm_token.emissionIntegral()
    dt = missionIntegralTx.timestamp - lastEmissionUpdateTimestamp
    assert missionIntegralTx.return_value == dt * \
        expected_yearEmission / SECONDS_IN_YEAR, "invalid emissionIntegral"


def test_yearEmission_beforeStartEmission(farm_token):
    assert_emission(farm_token, 0)


def test_yearEmission_inNextYear_beforeStartEmission(farm_token, chain):
    chain.mine(100, None, EMISSION_REDUCTION_SECONDS + 100)
    test_yearEmission_beforeStartEmission(farm_token)


def test_success_startEmission(farm_token, deployer, chain):
    t1 = chain.time()
    farm_token.startEmission({'from': deployer})
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()
    startEmissionTimestamp = farm_token.startEmissionTimestamp()
    t2 = chain.time()

    assert lastEmissionUpdateTimestamp >= t1 and lastEmissionUpdateTimestamp <= t2
    assert startEmissionTimestamp >= t1 and startEmissionTimestamp <= t2
    assert_emission(farm_token, INITIAL_EMISSION_RAW)


def test_emissionIntegral_progress(farm_token, chain, trinity, deployer, ZERO_ADDRESS):
    lastEmissionUpdateTimestamp = farm_token.lastEmissionUpdateTimestamp()

    for quarter in range(1, 12):  # 3 years
        old_emission_integral = farm_token.emissionIntegral().return_value

        time_move = quarter * SECONDS_IN_YEAR / 4
        chain.mine(100, lastEmissionUpdateTimestamp + time_move)

        year_emission = farm_token.yearEmission().return_value
        quater_max_minting_amount = year_emission / 4

        # emission integral always increase its' value
        emission_integral = farm_token.emissionIntegral().return_value
        assert emission_integral > old_emission_integral, "current emissionIntegral value must be greater than prev: quarter={quarter} time_move={time_move}"

        # mint process affects user's balance and total supply
        balance_before = farm_token.balanceOf(trinity)
        total_supply = farm_token.totalSupply()

        mint_tx = farm_token.mint(
            trinity, quater_max_minting_amount, {'from': deployer})
        assert len(mint_tx.events) == 1
        assert mint_tx.events["Transfer"].values(
        ) == [ZERO_ADDRESS, trinity, quater_max_minting_amount]

        assert farm_token.balanceOf(trinity) == balance_before + \
            quater_max_minting_amount, "minting process affects user's balance: quarter={quarter}"
        assert farm_token.totalSupply() == total_supply + \
            quater_max_minting_amount, "minting process affects total supply: quarter={quarter}"

        # fail to mint more than allowed
        with brownie.reverts("exceeds allowable mint amount"):
            farm_token.mint(trinity, to_raw_farm_token(100),
                            {'from': deployer})


def test_emission_overflow(farm_token, deployer, trinity):
    amount = farm_token.yearEmission().return_value + 1
    with brownie.reverts("exceeds allowable mint amount"):
        farm_token.mint(trinity, amount, {'from': deployer})


@ given(amount=strategy('uint256', min_value=1))
def test_mint_zero_address(ZERO_ADDRESS, farm_token, deployer, amount):
    with brownie.reverts("zero address"):
        farm_token.mint(ZERO_ADDRESS, amount, {'from': deployer})
