from brownie import (
    project,
    accounts,
    ERC20Basic,
    FarmToken,
    StakableERC20,
    Controller,
    VotingController,
    FarmTokenVotingStrategy,
    Reaper,
)
from pathlib import Path
from . import utils


INIT_SUPPLY = 1_000_000

DEPLOYER = accounts[2]
DAY = 86400
WEEK = DAY * 7

USDN_DECIMALS = 18
CURVE_DECIMALS = 18
USDT_DECIMALS = 6
USDC_DECIMALS = 6
DAI_DECIMALS = 18
DFT_DECIMALS = 18
MPOOL_LP_DECIMALS = 18
USDN_MPOOL_LP_DECIMALS = 18


def deploy():
    curve = utils.load_package('curvefi/curve-contract@1.0')
    curve_dao = utils.load_package('curvefi/curve-dao-contracts@1.1.0')
    uniswap = utils.load_package('Uniswap/uniswap-v2-core@1.0.1')

    usdn = deploy_usdn()
    usdt = deploy_erc20("Tether USD", "USDT", USDT_DECIMALS, INIT_SUPPLY)
    usdc = deploy_erc20("USD Coin", "USDC", USDC_DECIMALS, INIT_SUPPLY)
    dai = deploy_erc20("Dai Stablecoin", "DAI", DAI_DECIMALS, INIT_SUPPLY)
    crv = curve_dao.ERC20CRV.deploy(
        "Curve DAO Token", "CRV", CURVE_DECIMALS, {'from': DEPLOYER})
    dft = FarmToken.deploy("Dispersion Farming Token",
                           "DFT", DFT_DECIMALS, 20_000, {'from': DEPLOYER})

    # Uniswap
    uniswap_factory = uniswap.UniswapV2Factory.deploy(
        DEPLOYER, {'from': DEPLOYER})
    usdn_usdt_lp = uniswap_factory.createPair.call(usdn, usdt)  # USDN/USDT
    usdn_crv_lp = uniswap_factory.createPair.call(usdn, crv)   # USDN/CRV

    # Curve
    mpool_lp = curve.CurveTokenV2.deploy(
        "Curve.fi DAI/USDC/USDT", "3Crv", MPOOL_LP_DECIMALS, 0, {'from': DEPLOYER})
    mpool = curve.StableSwap3Pool.deploy(
        DEPLOYER, [dai, usdc, usdt], mpool_lp, 200, 4000000, 5000000000, {'from': DEPLOYER})
    mpool_lp.set_minter(mpool, {'from': DEPLOYER})
    dai.approve(mpool, 1000 * 10 ** DAI_DECIMALS, {'from': DEPLOYER})
    usdc.approve(mpool, 1000 * 10 ** USDC_DECIMALS, {'from': DEPLOYER})
    usdt.approve(mpool, 1000 * 10 ** USDT_DECIMALS, {'from': DEPLOYER})
    mpool.add_liquidity([
        1000 * 10 ** DAI_DECIMALS,
        1000 * 10 ** USDC_DECIMALS,
        1000 * 10 ** USDT_DECIMALS
    ], 0)

    usdn_mpool_lp = curve.CurveTokenV2.deploy(
        "Curve.fi USDN/3Crv", "usdn3CRV", USDN_MPOOL_LP_DECIMALS, 0, {'from': DEPLOYER})
    usdn_mpool = curve.StableSwapUSDN.deploy(
        DEPLOYER, [usdn, mpool_lp], usdn_mpool_lp, mpool, 100, 4000000, 0, {'from': DEPLOYER})
    usdn_mpool_lp.set_minter(usdn_mpool, {'from': DEPLOYER})
    deposit_usdn_mpool = curve.DepositUSDN.deploy(
        usdn_mpool, usdn_mpool_lp, {'from': DEPLOYER})
    usdn.approve(deposit_usdn_mpool, 1000 * 10 **
                 USDN_DECIMALS, {'from': DEPLOYER})
    dai.approve(deposit_usdn_mpool, 1000 * 10 **
                DAI_DECIMALS, {'from': DEPLOYER})
    usdc.approve(deposit_usdn_mpool, 1000 * 10 **
                 USDC_DECIMALS, {'from': DEPLOYER})
    usdt.approve(deposit_usdn_mpool, 1000 * 10 **
                 USDT_DECIMALS, {'from': DEPLOYER})
    deposit_usdn_mpool.add_liquidity([
        1000 * 10 ** USDN_DECIMALS,
        1000 * 10 ** DAI_DECIMALS,
        1000 * 10 ** USDC_DECIMALS,
        1000 * 10 ** USDT_DECIMALS
    ], 0)

    curve_voting_escrow = curve_dao.VotingEscrow.deploy(
        crv, 'Vote-escrowed CRV', 'veCRV', 'veCRV_1.0.0', {'from': DEPLOYER})
    curve_controller = curve_dao.GaugeController.deploy(
        crv, curve_voting_escrow, {'from': DEPLOYER})
    curve_minter = curve_dao.Minter.deploy(
        crv, curve_controller, {'from': DEPLOYER})
    usdn_mpool_gauge = curve_dao.LiquidityGauge.deploy(
        usdn_mpool_lp, curve_minter, DEPLOYER, {'from': DEPLOYER})
    curve_controller.add_type(
        "simple", 1000000000000000000, {'from': DEPLOYER})
    curve_controller.add_gauge(
        usdn_mpool_gauge, 0, 1000000000000000000, {'from': DEPLOYER})

    # Dispersion
    controller = Controller.deploy(dft, {'from': DEPLOYER})
    dft.setMinter(controller, {'from': DEPLOYER})

    voting_controller = VotingController.deploy(controller, {'from': DEPLOYER})
    dft_voting_strategy = FarmTokenVotingStrategy.deploy(
        voting_controller, dft, 1, WEEK, {'from': DEPLOYER})
    voting_controller.setVotingStrategy(
        dft, dft_voting_strategy, {'from': DEPLOYER})

    # Reapers
    usdn_usdt_reaper = Reaper.deploy(
        usdn_usdt_lp, dft, controller, voting_controller, 15, {'from': DEPLOYER})   # 1,5%
    controller.addReaper(usdn_usdt_reaper, {'from': DEPLOYER})
    usdn_crv_reaper = Reaper.deploy(
        usdn_crv_lp, dft, controller, voting_controller, 25, {'from': DEPLOYER})    # 2,5%
    controller.addReaper(usdn_crv_reaper, {'from': DEPLOYER})
    usdn_mpool_reaper = Reaper.deploy(
        usdn_mpool_lp, dft, controller, voting_controller, 42, {'from': DEPLOYER})  # 4,2%
    controller.addReaper(usdn_mpool_reaper, {'from': DEPLOYER})


def deploy_erc20(name, symbol, decimals, mint):
    token = ERC20Basic.deploy(name, symbol, decimals, 0, {'from': DEPLOYER})
    for account in accounts:
        token.mint(account, mint * 10 ** decimals, {'from': DEPLOYER})
    return token


def deploy_usdn():
    usdn = StakableERC20.deploy(
        "Neutrino USD", "USDN", USDN_DECIMALS, {'from': DEPLOYER})
    for account in accounts:
        usdn.deposit(account, INIT_SUPPLY * 10 **
                     USDN_DECIMALS, {'from': DEPLOYER})
    return usdn


def deploy_crv(curve):
    crv = curve.CurveTokenV2.deploy(
        "Curve DAO Token", "CRV", CURVE_DECIMALS, INIT_SUPPLY * len(accounts), {'from': DEPLOYER})
    for account in accounts[1:]:
        crv.transfer(account, INIT_SUPPLY * 10 **
                     CURVE_DECIMALS, {'from': DEPLOYER})
    return crv
