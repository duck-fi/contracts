# @version ^0.2.0


@view
@external
def adminFee() -> uint256:
    return 0


@view
@external
def lpToken() -> address:
    return ZERO_ADDRESS


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@view
@external
def controller() -> address:
    return ZERO_ADDRESS


@view
@external
def reaperStrategy() -> address:
    return ZERO_ADDRESS


@view
@external
def votingController() -> address:
    return ZERO_ADDRESS


@view
@external
def balances(_account: address) -> uint256:
    return 0


@view
@external
def depositAllowance(_owner: address, _spender: address) -> uint256:
    return 0


@view
@external
def totalBalances() -> uint256:
    return 0


@view
@external
def isKilled() -> bool:
    return False


@view
@external
def reapIntegral() -> uint256:
    return 0


@view
@external
def unitCostIntegral() -> uint256:
    return 0


@view
@external
def emissionIntegral() -> uint256:
    return 0


@view
@external
def voteIntegral() -> uint256:
    return 0


@view
@external
def reapIntegralFor(_account: address) -> uint256:
    return 0


@view
@external
def lastUnitCostIntegralFor(_account: address) -> uint256:
    return 0


@external
def depositApprove(_spender: address, _amount: uint256):
    pass


@external
def deposit(_amount: uint256, _account: address, _feeOptimization: bool, _gasToken: address):
    pass


@external
def invest(_gasToken: address):
    pass


@external
def reap(_gasToken: address):
    pass


@external
def withdraw(_amount: uint256, _gasToken: address):
    pass


@external
def snapshot(_account: address, _gasToken: address):
    pass


@external
def setReaperStrategy(_reaperStrategy: address):
    pass


@external
def kill():
    pass


@external
def setAdminFee(_percent: uint256):
    pass
