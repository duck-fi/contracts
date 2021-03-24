# @version ^0.2.11


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@view
@external
def boostingToken() -> address:
    return ZERO_ADDRESS


@view
@external
def boostIntegral() -> uint256:
    return 0


@view
@external
def balances(_coin: address, _account: address) -> uint256:
    return 0


@view
@external
def coinBalances(_coin: address) -> uint256:
    return 0


@external
def boost(_coin: address, _amount: uint256, _lockTime: uint256, _gasToken: address):
    pass


@external
def unboost(_coin: address, _gasToken: address):
    pass


@view
@external
def availableToUnboost(_coin: address, _account: address) -> uint256:
    return 0


@external
def accountBoostIntegral(_account: address) -> uint256:
    return 0


@external
def updateBoostIntegral() -> uint256:
    return 0
