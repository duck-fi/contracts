from brownie import (
    project,
    accounts,
    ERC20Basic,
    FarmToken,
    StakableERC20,
    Minter,
    Reaper,
    ReaperController,
    VotingController,
    SimpleVotingStrategy,
)
from pathlib import Path
from . import utils


DEPLOYER = accounts[2]
DAY = 86400
WEEK = DAY * 7

USDN_DECIMALS = 18
CURVE_DECIMALS = 18
USDT_DECIMALS = 6
USDC_DECIMALS = 6
DAI_DECIMALS = 18


def deploy():
    usdn = deploy_usdn()

    usdt = deploy_erc20("Tether USD", "USDT", USDT_DECIMALS, 1_000_000)
    usdc = deploy_erc20("USD Coin", "USDC", USDC_DECIMALS, 1_000_000)
    dai = deploy_erc20("Dai Stablecoin", "DAI", DAI_DECIMALS, 1_000_000)
    crv = deploy_crv()
    dft = FarmToken.deploy("Dispersion Farming Token",
                           "DFT", 18, 20_000, {'from': DEPLOYER})

    # Uniswap
    uniswap_factory = deploy_uniswap_factory()
    uniswap_factory.createPair(usdn, usdt)  # USDN/USDT
    uniswap_factory.createPair(usdn, crv)   # USDN/CRV

    # deployCurveContracts()
    # deployUniswapContracts()

    # minter = Minter.deploy(farm_token, {'from': DEPLOYER})
    # farm_token.setMinter(minter, {'from': DEPLOYER})

    # reaper_controller = ReaperController.deploy(minter, {'from': DEPLOYER})
    # minter.setReaperController(reaper_controller, {'from': DEPLOYER})

    # # Voting
    # voting_controller = VotingController.deploy(
    #     reaper_controller, {'from': DEPLOYER})
    # simple_voting_strategy = SimpleVotingStrategy.deploy(
    #     farm_token, 1, DAY, {'from': DEPLOYER})
    # voting_controller.setStrategy(
    #     farm_token, simple_voting_strategy, {'from': DEPLOYER})

    # Reapers
    # uniswapReaper = Reaper.deploy(_lp_token: address, reaper_controller, voting_controller, {'from': DEPLOYER})
    # minter.setReaperController(reaperController, {'from': DEPLOYER})


def deploy_erc20(name, symbol, decimals, mint):
    token = ERC20Basic.deploy(name, symbol, decimals, 0, {'from': DEPLOYER})
    for account in accounts:
        token.mint(account, mint * 10 ** decimals, {'from': DEPLOYER})
    return token


def deploy_usdn():
    usdn = StakableERC20.deploy(
        "Neutrino USD", "USDN", USDN_DECIMALS, {'from': DEPLOYER})
    for account in accounts:
        usdn.deposit(account, 1_000_000 * 10 **
                     USDN_DECIMALS, {'from': DEPLOYER})
    return usdn


def deploy_uniswap_factory():
    uniswap = utils.load_package('Uniswap/uniswap-v2-core@1.0.1')
    return uniswap.UniswapV2Factory.deploy(DEPLOYER, {'from': DEPLOYER})


def deploy_crv():
    curve = utils.load_package('curvefi/curve-dao-contracts@1.1.0')
    crv = curve.ERC20CRV.deploy(
        "Curve DAO Token", "CRV", CURVE_DECIMALS, {'from': DEPLOYER})
    return crv
