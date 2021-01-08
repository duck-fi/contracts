from brownie import (
    accounts,
    FarmToken,
    BasicMinter
)


DEPLOYER = accounts[0]


def deploy():
    farm_token = FarmToken.deploy("Dispersion Farming Token",
                                  "DFT", 18, 0, {'from': DEPLOYER})

    minter = BasicMinter.deploy(farm_token, {'from': DEPLOYER})
    farm_token.setMinter(minter, {'from': DEPLOYER})
