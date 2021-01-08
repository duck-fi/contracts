from brownie import (
    accounts,
    FarmToken
)


DEPLOYER = accounts[0]


def deploy():
    FarmToken.deploy("Dispersion Farming Token",
                     "DFT", 18, 0, {'from': DEPLOYER})
