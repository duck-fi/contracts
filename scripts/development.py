from brownie import (
    project,
    accounts,
    ERC20,
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


def deploy():
    usdn = deploy_usdn()
    # usdt = deploy_tether()
    dft = FarmToken.deploy("Dispersion Farming Token",
                           "DFT", 18, 20_000, {'from': DEPLOYER})

    # Uniswap
    # uniswap_factory = deployUniswapFactory()
    # uniswap_factory.createPair(usdn, usdt) # USDN/USDT

#     deployCurveContracts()
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


def deploy_tether():
    tether_token = ERC20.deploy(
        "Tether USD", "USDT", 6, 0, {'from': DEPLOYER})
    for i in range(10):
        tether_token.mint(accounts[i], 1_000_000 * 10 ** 6, {'from': DEPLOYER})
    return tether_token


def deploy_usdn():
    usdn_token = StakableERC20.deploy(
        "Neutrino USD", "USDN", 18, {'from': DEPLOYER})
    for account in accounts:
        usdn_token.deposit(account, 1_000_000 * 10 ** 18, {'from': DEPLOYER})
    return usdn_token


def deployUniswapFactory():
    uniswap = utils.load_package('Uniswap/uniswap-v2-core@1.0.1')
    return uniswap.UniswapV2Factory.deploy(DEPLOYER, {'from': DEPLOYER})


# def deployCurveContracts():
#     package = 'curvefi/curve-dao-contracts@1.0.0'
#     aaa = project.load(Path.home().joinpath(".brownie").joinpath(f"packages/curvefi/curve-dao-contracts@1.1.0"), 'curvefi/curve-dao-contracts@1.1.0').ERC20CRV
#     crvToken = pm('curvefi/curve-dao-contracts@1.0.0').deploy({'from': DEPLOYER})
#     assert crvToken.total_supply() == 0
