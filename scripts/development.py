from brownie import (
    accounts,
    FarmToken,
    Minter,
    Reaper,
    ReaperController,
    VotingController,
    SimpleVotingStrategy
)


DEPLOYER = accounts[2]
DAY = 86400
WEEK = DAY * 7


def deploy():
    farm_token = FarmToken.deploy("Dispersion Farming Token",
                                  "DFT", 18, 1000, {'from': DEPLOYER})

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
