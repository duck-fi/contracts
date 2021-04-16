from brownie import (
    project,
    accounts,
    ERC20Basic,
    FarmToken,
    StrictTransferableToken,
    StakableERC20,
    Controller,
    VotingController,
    BoostingController,
    Reaper,
    WhiteList
)
from pathlib import Path
from . import utils


INIT_SUPPLY = 100_000_000

DEPLOYER = accounts[2]
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


def deploy():
    curve = utils.load_package('curvefi/curve-contract@1.0')
    curve_dao = utils.load_package('curvefi/curve-dao-contracts@1.1.0')
    uniswap = utils.load_package('Uniswap/uniswap-v2-core@1.0.1')
    chi = utils.load_package('forest-friends/chi@1.0.1')

    usdn = deploy_usdn()
    usdt = deploy_erc20("Tether USD", "USDT", USDT_DECIMALS, INIT_SUPPLY)
    usdc = deploy_erc20("USD Coin", "USDC", USDC_DECIMALS, INIT_SUPPLY)
    dai = deploy_erc20("Dai Stablecoin", "DAI", DAI_DECIMALS, INIT_SUPPLY)
    weth = deploy_erc20("Wrapped Ether", "WETH", WETH_DECIMALS, INIT_SUPPLY)
    crv = curve_dao.ERC20CRV.deploy(
        "Curve DAO Token", "CRV", CURVE_DECIMALS, {'from': DEPLOYER})
    ducks = FarmToken.deploy("DUCKS Farming Token",
                             "DUCKS", {'from': DEPLOYER})
    chi_token = chi.ChiToken.deploy({'from': DEPLOYER})

    # Uniswap
    uniswap_factory = uniswap.UniswapV2Factory.deploy(
        DEPLOYER, {'from': DEPLOYER})

    # USDN/USDT
    usdn_usdt_lp = uniswap_factory.createPair(
        usdn, usdt, {'from': DEPLOYER}).return_value
    usdn.transfer(usdn_usdt_lp, 5_000_000 * 10 ** USDN_DECIMALS, {'from': DEPLOYER})
    usdt.transfer(usdn_usdt_lp, 5_000_000 * 10 ** USDT_DECIMALS, {'from': DEPLOYER})
    uniswap.interface.IUniswapV2Pair(
        usdn_usdt_lp).mint(DEPLOYER, {'from': DEPLOYER})

    # USDN/CRV
    usdn_crv_lp = uniswap_factory.createPair(
        usdn, crv, {'from': DEPLOYER}).return_value
    usdn.transfer(usdn_crv_lp, 1000 * 10 ** USDN_DECIMALS, {'from': DEPLOYER})
    crv.transfer(usdn_crv_lp, 500 * 10 ** CURVE_DECIMALS, {'from': DEPLOYER})
    uniswap.interface.IUniswapV2Pair(
        usdn_crv_lp).mint(DEPLOYER, {'from': DEPLOYER})

    # USDN/DUCKS
    usdn_ducks_lp = uniswap_factory.createPair(
        usdn, ducks, {'from': DEPLOYER}).return_value
    usdn.transfer(usdn_ducks_lp, 1000 * 10 **
                  USDN_DECIMALS, {'from': DEPLOYER})
    ducks.transfer(usdn_ducks_lp, 50 * 10 **
                   DUCKS_DECIMALS, {'from': DEPLOYER})
    uniswap.interface.IUniswapV2Pair(
        usdn_ducks_lp).mint(DEPLOYER, {'from': DEPLOYER})

    # USDN/WETH
    usdn_weth_lp = uniswap_factory.createPair(
        usdn, weth, {'from': DEPLOYER}).return_value
    usdn.transfer(usdn_weth_lp, 5_000_000 * 10 **
                  USDN_DECIMALS, {'from': DEPLOYER})
    weth.transfer(usdn_weth_lp, 5_000 * 10 **
                  WETH_DECIMALS, {'from': DEPLOYER})
    uniswap.interface.IUniswapV2Pair(
        usdn_weth_lp).mint(DEPLOYER, {'from': DEPLOYER})

    # Curve
    mpool_lp = curve.CurveTokenV2.deploy(
        "Curve.fi DAI/USDC/USDT", "3Crv", MPOOL_LP_DECIMALS, 0, {'from': DEPLOYER})
    mpool = curve.StableSwap3Pool.deploy(
        DEPLOYER, [dai, usdc, usdt], mpool_lp, 200, 4000000, 5000000000, {'from': DEPLOYER})
    mpool_lp.set_minter(mpool, {'from': DEPLOYER})
    dai.approve(mpool, 2_000_000 * 10 ** DAI_DECIMALS, {'from': DEPLOYER})
    usdc.approve(mpool, 2_000_000 * 10 ** USDC_DECIMALS, {'from': DEPLOYER})
    usdt.approve(mpool, 2_000_000 * 10 ** USDT_DECIMALS, {'from': DEPLOYER})
    mpool.add_liquidity([
        2_000_000 * 10 ** DAI_DECIMALS,
        2_000_000 * 10 ** USDC_DECIMALS,
        2_000_000 * 10 ** USDT_DECIMALS
    ], 0)

    usdn_mpool_lp = curve.CurveTokenV2.deploy(
        "Curve.fi USDN/3Crv", "usdn3CRV", USDN_MPOOL_LP_DECIMALS, 0, {'from': DEPLOYER})
    usdn_mpool = curve.StableSwapUSDN.deploy(
        DEPLOYER, [usdn, mpool_lp], usdn_mpool_lp, mpool, 100, 4000000, 0, {'from': DEPLOYER})
    usdn_mpool_lp.set_minter(usdn_mpool, {'from': DEPLOYER})
    deposit_usdn_mpool = curve.DepositUSDN.deploy(
        usdn_mpool, usdn_mpool_lp, {'from': DEPLOYER})
    usdn.approve(deposit_usdn_mpool, 3_000_000 * 10 **
                 USDN_DECIMALS, {'from': DEPLOYER})
    dai.approve(deposit_usdn_mpool, 1_000_000 * 10 **
                DAI_DECIMALS, {'from': DEPLOYER})
    usdc.approve(deposit_usdn_mpool, 1_000_000 * 10 **
                 USDC_DECIMALS, {'from': DEPLOYER})
    usdt.approve(deposit_usdn_mpool, 1_000_000 * 10 **
                 USDT_DECIMALS, {'from': DEPLOYER})
    deposit_usdn_mpool.add_liquidity([
        3_000_000 * 10 ** USDN_DECIMALS,
        1_000_000 * 10 ** DAI_DECIMALS,
        1_000_000 * 10 ** USDC_DECIMALS,
        1_000_000 * 10 ** USDT_DECIMALS
    ], 0, {'from': DEPLOYER})

    curve_voting_escrow = curve_dao.VotingEscrow.deploy(
        crv, 'Vote-escrowed CRV', 'veCRV', 'veCRV_1.0.0', {'from': DEPLOYER})
    curve_controller = curve_dao.GaugeController.deploy(
        crv, curve_voting_escrow, {'from': DEPLOYER})
    curve_minter = curve_dao.Minter.deploy(
        crv, curve_controller, {'from': DEPLOYER})
    usdn_mpool_gauge = curve_dao.LiquidityGauge.deploy(
        usdn_mpool_lp, curve_minter, DEPLOYER, {'from': DEPLOYER})
    curve_controller.add_type(
        "simple", 10 ** 18, {'from': DEPLOYER})
    curve_controller.add_gauge(
        usdn_mpool_gauge, 0, 10 ** 18, {'from': DEPLOYER})

    # Dispersion
    gas_token_check_list = WhiteList.deploy({'from': DEPLOYER})
    gas_token_check_list.addAddress(chi_token, {'from': DEPLOYER})

    controller = Controller.deploy(
        ducks, gas_token_check_list, {'from': DEPLOYER})
    ducks.setMinter(controller, {'from': DEPLOYER})

    voting_controller = VotingController.deploy(
        controller, gas_token_check_list, ducks, {'from': DEPLOYER})
    vducks_minter_check_list = WhiteList.deploy({'from': DEPLOYER})
    vducks = StrictTransferableToken.deploy("DUCKS Voting Token",
                                          "vDUCKS", vducks_minter_check_list, voting_controller, {'from': DEPLOYER})
    voting_controller.setVotingToken(vducks, {'from': DEPLOYER})

    boosting_controller = BoostingController.deploy(
        gas_token_check_list, {'from': DEPLOYER})
    bducks_minter_check_list = WhiteList.deploy({'from': DEPLOYER})
    bducks = StrictTransferableToken.deploy("DUCKS Boosting Token",
                                          "bDUCKS", bducks_minter_check_list, boosting_controller, {'from': DEPLOYER})

    # Reapers
    usdn_usdt_reaper = Reaper.deploy(
        usdn_usdt_lp, ducks, controller, voting_controller, boosting_controller, gas_token_check_list, 15, {'from': DEPLOYER})   # 1,5%
    controller.addReaper(usdn_usdt_reaper, {'from': DEPLOYER})
    usdn_weth_reaper = Reaper.deploy(
        usdn_weth_lp, ducks, controller, voting_controller, boosting_controller, gas_token_check_list, 25, {'from': DEPLOYER})    # 2,5%
    controller.addReaper(usdn_weth_reaper, {'from': DEPLOYER})
    usdn_mpool_reaper = Reaper.deploy(
        usdn_mpool_lp, ducks, controller, voting_controller, boosting_controller, gas_token_check_list, 42, {'from': DEPLOYER})  # 4,2%
    controller.addReaper(usdn_mpool_reaper, {'from': DEPLOYER})

    # Deposit to reapers
    usdn_usdt_lp_balance = uniswap.interface.IUniswapV2ERC20(usdn_usdt_lp).balanceOf(DEPLOYER, {'from': DEPLOYER})
    uniswap.interface.IUniswapV2ERC20(usdn_usdt_lp).approve(usdn_usdt_reaper, usdn_usdt_lp_balance, {'from': DEPLOYER})
    usdn_usdt_reaper.deposit(usdn_usdt_lp_balance, {'from': DEPLOYER})

    usdn_weth_lp_balance = uniswap.interface.IUniswapV2ERC20(usdn_weth_lp).balanceOf(DEPLOYER, {'from': DEPLOYER})
    uniswap.interface.IUniswapV2ERC20(usdn_weth_lp).approve(usdn_weth_reaper, usdn_weth_lp_balance, {'from': DEPLOYER})
    usdn_weth_reaper.deposit(usdn_weth_lp_balance, {'from': DEPLOYER})

    usdn_mpool_lp_balance = usdn_mpool_lp.balanceOf(DEPLOYER, {'from': DEPLOYER})
    usdn_mpool_lp.approve(usdn_mpool_reaper, usdn_mpool_lp_balance, {'from': DEPLOYER})
    usdn_mpool_reaper.deposit(usdn_mpool_lp_balance, {'from': DEPLOYER})

    # Dispersion start emission
    controller.startEmission(voting_controller, 0)

    print("usdn_usdt_lp_balance: {}".format(usdn_usdt_lp_balance))
    print("usdn_weth_lp_balance: {}".format(usdn_weth_lp_balance))
    print("usdn_mpool_lp_balance: {}".format(usdn_mpool_lp_balance))
    print("DUCKS: {}".format(ducks))
    print("USDN: {}".format(usdn))
    print("USDT: {}".format(usdt))
    print("USDC: {}".format(usdc))
    print("DAI: {}".format(dai))
    print("WETH: {}".format(weth))
    print("CRV: {}".format(crv))
    print("CHI: {}".format(chi_token))
    print("UNI USDN/CRV: {}".format(usdn_crv_lp))
    print("UNI USDN/USDT: {}".format(usdn_usdt_lp))
    print("UNI USDN/DUCKS: {}".format(usdn_ducks_lp))
    print("UNI USDN/WETH: {}".format(usdn_weth_lp))
    print("CURVE USDN/3POOL: {}".format(usdn_mpool))
    print("REAPER USDN/USDT: {}".format(usdn_usdt_reaper))
    print("REAPER USDN/WETH: {}".format(usdn_weth_reaper))
    print("REAPER USDN/3POOL: {}".format(usdn_mpool_reaper))


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
