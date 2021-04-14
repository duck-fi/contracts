from brownie import (
    project,
    accounts,
    chain,
    ERC20Basic,
    FarmToken,
    StrictTransferableToken,
    StakableERC20,
    Controller,
    VotingController,
    BoostingController,
    Reaper,
    WhiteList,
    CurveStaker,
    CurveReaperStrategyV1,
    UniswapReaperStrategyV1
)
from pathlib import Path
import pytest


INIT_SUPPLY = 1_000_000

DAY = 86400
WEEK = DAY * 7

USDN_DECIMALS = 18
CURVE_DECIMALS = 18
USDT_DECIMALS = 6
USDC_DECIMALS = 6
DAI_DECIMALS = 18
WETH_DECIMALS = 18
DUCKS_DECIMALS = 18
MPOOL_LP_DECIMALS = 18
USDN_MPOOL_LP_DECIMALS = 18


@pytest.fixture(scope="module")
def farm_contracts(deployer, pm):
    contracts = {}

    curve = pm('curvefi/curve-contract@1.0')
    curve_dao = pm('curvefi/curve-dao-contracts@1.1.0')
    uniswap = pm('Uniswap/uniswap-v2-core@1.0.1')
    # uniswap_peripheral = pm('Uniswap/uniswap-v2-periphery@1.0.0-beta.0') TODO: remove
    chi = pm('forest-friends/chi@1.0.1')

    usdn = deploy_usdn(deployer)
    usdt = deploy_erc20("Tether USD", "USDT", USDT_DECIMALS, INIT_SUPPLY, deployer)
    usdc = deploy_erc20("USD Coin", "USDC", USDC_DECIMALS, INIT_SUPPLY, deployer)
    dai = deploy_erc20("Dai Stablecoin", "DAI", DAI_DECIMALS, INIT_SUPPLY, deployer)
    weth = deploy_erc20("Wrapped Ether", "WETH", WETH_DECIMALS, INIT_SUPPLY, deployer)
    crv = curve_dao.ERC20CRV.deploy(
        "Curve DAO Token", "CRV", CURVE_DECIMALS, {'from': deployer})
    chain.mine(1, chain.time() + 86400) # wait a day for start crv emission
    crv.update_mining_parameters({'from': deployer}) # start crv emission
    ducks = FarmToken.deploy("DUCKS Farming Token",
                             "DUCKS", {'from': deployer})
    chi_token = chi.ChiToken.deploy({'from': deployer})

    # Uniswap
    uniswap_factory = uniswap.UniswapV2Factory.deploy(
        deployer, {'from': deployer})
    # uniswap_router_v2 = uniswap_peripheral.UniswapV2Router02.deploy({'from': deployer})  TODO: remove

    # USDN/USDT
    usdn_usdt_lp = uniswap_factory.createPair(
        usdn, usdt, {'from': deployer}).return_value
    usdn.transfer(usdn_usdt_lp, 1000 * 10 ** USDN_DECIMALS, {'from': deployer})
    usdt.transfer(usdn_usdt_lp, 1000 * 10 ** USDT_DECIMALS, {'from': deployer})
    uniswap.interface.IUniswapV2Pair(
        usdn_usdt_lp).mint(deployer, {'from': deployer})

    # USDN/CRV
    usdn_crv_lp = uniswap_factory.createPair(
        usdn, crv, {'from': deployer}).return_value
    usdn.transfer(usdn_crv_lp, 1000 * 10 ** USDN_DECIMALS, {'from': deployer})
    crv.transfer(usdn_crv_lp, 500 * 10 ** CURVE_DECIMALS, {'from': deployer})
    uniswap.interface.IUniswapV2Pair(
        usdn_crv_lp).mint(deployer, {'from': deployer})

    # USDN/DUCKS
    usdn_ducks_lp = uniswap_factory.createPair(
        usdn, ducks, {'from': deployer}).return_value
    usdn.transfer(usdn_ducks_lp, 1000 * 10 **
                  USDN_DECIMALS, {'from': deployer})
    ducks.transfer(usdn_ducks_lp, 50 * 10 **
                   DUCKS_DECIMALS, {'from': deployer})
    uniswap.interface.IUniswapV2Pair(
        usdn_ducks_lp).mint(deployer, {'from': deployer})

    # USDN/WETH
    usdn_weth_lp = uniswap_factory.createPair(
        usdn, weth, {'from': deployer}).return_value
    usdn.transfer(usdn_weth_lp, 1000 * 10 **
                  USDN_DECIMALS, {'from': deployer})
    weth.transfer(usdn_weth_lp, 1 * 10 **
                  WETH_DECIMALS, {'from': deployer})
    uniswap.interface.IUniswapV2Pair(
        usdn_weth_lp).mint(deployer, {'from': deployer})

    # Curve
    mpool_lp = curve.CurveTokenV2.deploy(
        "Curve.fi DAI/USDC/USDT", "3Crv", MPOOL_LP_DECIMALS, 0, {'from': deployer})
    mpool = curve.StableSwap3Pool.deploy(
        deployer, [dai, usdc, usdt], mpool_lp, 200, 4000000, 5000000000, {'from': deployer})
    mpool_lp.set_minter(mpool, {'from': deployer})
    dai.approve(mpool, 1000 * 10 ** DAI_DECIMALS, {'from': deployer})
    usdc.approve(mpool, 1000 * 10 ** USDC_DECIMALS, {'from': deployer})
    usdt.approve(mpool, 1000 * 10 ** USDT_DECIMALS, {'from': deployer})
    mpool.add_liquidity([
        1000 * 10 ** DAI_DECIMALS,
        1000 * 10 ** USDC_DECIMALS,
        1000 * 10 ** USDT_DECIMALS
    ], 0)

    usdn_mpool_lp = curve.CurveTokenV2.deploy(
        "Curve.fi USDN/3Crv", "usdn3CRV", USDN_MPOOL_LP_DECIMALS, 0, {'from': deployer})
    usdn_mpool = curve.StableSwapUSDN.deploy(
        deployer, [usdn, mpool_lp], usdn_mpool_lp, mpool, 100, 4000000, 0, {'from': deployer})
    usdn_mpool_lp.set_minter(usdn_mpool, {'from': deployer})
    deposit_usdn_mpool = curve.DepositUSDN.deploy(
        usdn_mpool, usdn_mpool_lp, {'from': deployer})
    usdn.approve(deposit_usdn_mpool, 1_000 * 10 **
                 USDN_DECIMALS, {'from': deployer})
    dai.approve(deposit_usdn_mpool, 1_000 * 10 **
                DAI_DECIMALS, {'from': deployer})
    usdc.approve(deposit_usdn_mpool, 1_000 * 10 **
                 USDC_DECIMALS, {'from': deployer})
    usdt.approve(deposit_usdn_mpool, 1_000 * 10 **
                 USDT_DECIMALS, {'from': deployer})
    deposit_usdn_mpool.add_liquidity([
        1_000 * 10 ** USDN_DECIMALS,
        1_000 * 10 ** DAI_DECIMALS,
        1_000 * 10 ** USDC_DECIMALS,
        1_000 * 10 ** USDT_DECIMALS
    ], 0, {'from': deployer})

    curve_voting_escrow = curve_dao.VotingEscrow.deploy(
        crv, 'Vote-escrowed CRV', 'veCRV', 'veCRV_1.0.0', {'from': deployer})
    curve_controller = curve_dao.GaugeController.deploy(
        crv, curve_voting_escrow, {'from': deployer})
    curve_minter = curve_dao.Minter.deploy(
        crv, curve_controller, {'from': deployer})
    usdn_mpool_gauge = curve_dao.LiquidityGauge.deploy(
        usdn_mpool_lp, curve_minter, deployer, {'from': deployer})
    curve_controller.add_type(
        "simple", 10 ** 18, {'from': deployer})
    curve_controller.add_gauge(
        usdn_mpool_gauge, 0, 10 ** 18, {'from': deployer})

    # Duck finance
    gas_token_check_list = WhiteList.deploy({'from': deployer})
    gas_token_check_list.addAddress(chi_token, {'from': deployer})

    controller = Controller.deploy(
        ducks, gas_token_check_list, {'from': deployer})
    ducks.setMinter(controller, {'from': deployer})

    voting_controller = VotingController.deploy(
        controller, gas_token_check_list, ducks, {'from': deployer})
    vducks_minter_check_list = WhiteList.deploy({'from': deployer})
    vducks = StrictTransferableToken.deploy("DUCKS Voting Token",
                                          "vDUCKS", vducks_minter_check_list, voting_controller, {'from': deployer})
    voting_controller.setVotingToken(vducks, {'from': deployer})

    boosting_controller = BoostingController.deploy(
        gas_token_check_list, {'from': deployer})
    bducks_minter_check_list = WhiteList.deploy({'from': deployer})
    bducks = StrictTransferableToken.deploy("DUCKS Boosting Token",
                                          "bDUCKS", bducks_minter_check_list, boosting_controller, {'from': deployer})
    
    curve_staker = CurveStaker.deploy(usdn_mpool_gauge, usdn_mpool_lp, crv, curve_voting_escrow, {'from': deployer})

    # Reapers
    usdn_usdt_reaper = Reaper.deploy(
        usdn_usdt_lp, ducks, controller, voting_controller, boosting_controller, gas_token_check_list, 15, {'from': deployer})   # 1,5%
    controller.addReaper(usdn_usdt_reaper, {'from': deployer})
    usdn_weth_reaper = Reaper.deploy(
        usdn_weth_lp, ducks, controller, voting_controller, boosting_controller, gas_token_check_list, 25, {'from': deployer})    # 2,5%
    controller.addReaper(usdn_weth_reaper, {'from': deployer})
    usdn_mpool_reaper = Reaper.deploy(
        usdn_mpool_lp, ducks, controller, voting_controller, boosting_controller, gas_token_check_list, 42, {'from': deployer})  # 4,2%
    controller.addReaper(usdn_mpool_reaper, {'from': deployer})

    # Reaper strategies
    curve_strategy_v1 = CurveReaperStrategyV1.deploy(usdn_mpool_reaper, curve_staker, deployer, usdn, {'from': deployer}) # TODO: deployer -> uniswap_router_v2
    usdn_mpool_reaper.setReaperStrategy(curve_strategy_v1, {'from': deployer})
    curve_staker.setReaperStrategy(curve_strategy_v1, {'from': deployer})

    uniswap_strategy_v1 = UniswapReaperStrategyV1.deploy({'from': deployer})
    usdn_usdt_reaper.setReaperStrategy(uniswap_strategy_v1, {'from': deployer})
    usdn_weth_reaper.setReaperStrategy(uniswap_strategy_v1, {'from': deployer})

    # add tokens to dict
    contracts['usdn'] = usdn
    contracts['usdt'] = usdt
    contracts['usdc'] = usdc
    contracts['dai'] = dai
    contracts['weth'] = weth
    contracts['crv'] = crv
    contracts['ducks'] = ducks
    contracts['chi_token'] = chi_token

    # add uniswap to dict
    contracts['uniswap_factory'] = uniswap_factory
    contracts['usdn_usdt_lp'] = uniswap.interface.IUniswapV2Pair(usdn_usdt_lp)
    contracts['usdn_crv_lp'] = uniswap.interface.IUniswapV2Pair(usdn_crv_lp)
    contracts['usdn_ducks_lp'] = uniswap.interface.IUniswapV2Pair(usdn_ducks_lp)
    contracts['usdn_weth_lp'] = uniswap.interface.IUniswapV2Pair(usdn_weth_lp)

    # add curve pools to dict
    contracts['mpool_lp'] = mpool_lp
    contracts['mpool'] = mpool
    contracts['usdn_mpool_lp'] = usdn_mpool_lp
    contracts['usdn_mpool'] = usdn_mpool
    contracts['deposit_usdn_mpool'] = deposit_usdn_mpool

    # add curve dao to dict
    contracts['curve_voting_escrow'] = curve_voting_escrow
    contracts['curve_controller'] = curve_controller
    contracts['curve_minter'] = curve_minter
    contracts['usdn_mpool_gauge'] = usdn_mpool_gauge

    # add duck finance to dict
    contracts['gas_token_check_list'] = gas_token_check_list
    contracts['controller'] = controller
    contracts['voting_controller'] = voting_controller
    contracts['vducks_minter_check_list'] = vducks_minter_check_list
    contracts['vducks'] = vducks
    contracts['boosting_controller'] = boosting_controller
    contracts['bducks_minter_check_list'] = bducks_minter_check_list
    contracts['bducks'] = bducks
    contracts['curve_staker'] = curve_staker

    # add duck finance reapers to dict
    contracts['usdn_usdt_reaper'] = usdn_usdt_reaper
    contracts['usdn_weth_reaper'] = usdn_weth_reaper
    contracts['usdn_mpool_reaper'] = usdn_mpool_reaper
    contracts['curve_strategy_v1'] = curve_strategy_v1
    contracts['uniswap_strategy_v1'] = uniswap_strategy_v1

    yield contracts


def deploy_erc20(name, symbol, decimals, mint, deployer):
    token = ERC20Basic.deploy(name, symbol, decimals, 0, {'from': deployer})
    for account in accounts:
        token.mint(account, mint * 10 ** decimals, {'from': deployer})
    return token


def deploy_usdn(deployer):
    usdn = StakableERC20.deploy(
        "Neutrino USD", "USDN", USDN_DECIMALS, {'from': deployer})
    for account in accounts:
        usdn.deposit(account, INIT_SUPPLY * 10 **
                     USDN_DECIMALS, {'from': deployer})
    return usdn
