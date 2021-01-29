# @version ^0.2.0


@view
@external
def lpToken() -> address:
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


@external
def reapIntegral() -> uint256:
    return 0


@external
def emissionIntegral() -> uint256:
    return 0


@external
def voteIntegral() -> uint256:
    return 0


@external
def lastSnapshotTimestamp() -> uint256:
    return 0


@external
def reapIntegralFor(_account: address) -> uint256:
    return 0


@external
def lastReapTimestampFor(_account: address) -> uint256:
    return 0


@external
def rewardIntegral() -> uint256:
    return 0


@external
def rewardIntegralFor(_account: address) -> uint256:
    return 0


@external
def depositApprove(_spender: address, _amount:uint256):
    pass


@external
def deposit(_amount: uint256, _account: address, _feeOptimization: bool):
    pass


@external
def invest():
    pass


@external
def reap():
    pass


@external
def withdraw(_amount: uint256):
    pass


@external
def claim(_account: address):
    pass


@external
def claimableTokens(_account: address):
    pass


@external
def snapshot(_account: address):
    pass


@external
def setReaperStrategy(_reaperStrategy: address):
    pass


@external
def kill():
    pass
