from brownie import (
    accounts,
    FarmToken,
    Minter,
    Reaper,
    ReaperController
)


DEPLOYER = accounts[2]


def deploy():
    farm_token = FarmToken.deploy("Dispersion Farming Token",
                                  "DFT", 18, 1000, {'from': DEPLOYER})

    minter = Minter.deploy(farm_token, {'from': DEPLOYER})
    farm_token.setMinter(minter, {'from': DEPLOYER})

    reaperController = ReaperController.deploy(minter, {'from': DEPLOYER})
    minter.setReaperController(reaperController, {'from': DEPLOYER})

    # curveReaper = Reaper.deploy(minter, {'from': DEPLOYER})
    # minter.setReaperController(reaperController, {'from': DEPLOYER})
