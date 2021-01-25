from brownie import project
from pathlib import Path


BROWNIE_DIR_NAME = ".brownie"
BROWNIE_PATH = Path.home().joinpath(BROWNIE_DIR_NAME)


def load_package(package_name):
    return project.load(BROWNIE_PATH.joinpath(f'packages/{package_name}'), package_name)
