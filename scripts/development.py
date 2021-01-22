from brownie import (
    project,
    accounts,
    FarmToken,
    StakableERC20,
    Minter,
    Reaper,
    ReaperController,
    VotingController,
    SimpleVotingStrategy,
)
from pathlib import Path


DEPLOYER = accounts[2]
DAY = 86400
WEEK = DAY * 7


def deploy():
    usdn_token = StakableERC20.deploy("Neutrino USD", "USDN", 18, {'from': DEPLOYER})
    farm_token = FarmToken.deploy("Dispersion Farming Token", "DFT", 18, 1000, {'from': DEPLOYER})

#     deployCurveContracts()
    deployUniswapContracts()

    minter = Minter.deploy(farm_token, {'from': DEPLOYER})
    farm_token.setMinter(minter, {'from': DEPLOYER})

    reaper_controller = ReaperController.deploy(minter, {'from': DEPLOYER})
    minter.setReaperController(reaper_controller, {'from': DEPLOYER})

    # Voting
    voting_controller = VotingController.deploy(
        reaper_controller, {'from': DEPLOYER})
    simple_voting_strategy = SimpleVotingStrategy.deploy(
        farm_token, 1, DAY, {'from': DEPLOYER})
    voting_controller.setStrategy(
        farm_token, simple_voting_strategy, {'from': DEPLOYER})

    # Reapers
    # uniswapReaper = Reaper.deploy(_lp_token: address, reaper_controller, voting_controller, {'from': DEPLOYER})
    # minter.setReaperController(reaperController, {'from': DEPLOYER})


def deployCurveContracts():
    package = 'curvefi/curve-dao-contracts@1.0.0'
    aaa = project.load(Path.home().joinpath(".brownie").joinpath(f"packages/curvefi/curve-dao-contracts@1.1.0"), 'curvefi/curve-dao-contracts@1.1.0').ERC20CRV
    crvToken = pm('curvefi/curve-dao-contracts@1.0.0').deploy({'from': DEPLOYER})
    assert crvToken.total_supply() == 0


def deployUniswapContracts():
    package = 'Uniswap/uniswap-v2-core@1.0.1'
    uniswapProject = project.load(Path.home().joinpath(".brownie").joinpath(f"packages/Uniswap/uniswap-v2-core@1.0.1"), 'Uniswap/uniswap-v2-core@1.0.1')
    uniswapV2ERC20Token = uniswapProject.UniswapV2ERC20.deploy({'from': DEPLOYER})
#     uniswapV2Factory = uniswapProject.UniswapV2Factory.deploy(DEPLOYER, {'from': DEPLOYER})
#     pairToken = uniswapV2Factory.createPair(tokenA, tokenB)
