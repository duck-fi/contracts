# @version ^0.2.11


@view
@external
def controller() -> address:
    return ZERO_ADDRESS


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@view
@external
def votingToken() -> address:
    return ZERO_ADDRESS


@view
@external
def balances(_reaper: address, _coin: address, _account: address) -> uint256:
    return 0


@view
@external
def balancesUnlockTimestamp(_reaper: address, _coin: address, _account: address) -> uint256:
    return 0


@view
@external
def reaperBalances(_reaper: address, _coin: address) -> uint256:
    return 0


@view
@external
def lastVotes(_reaper: address) -> uint256:
    return 0


@view
@external
def reaperIntegratedVotes(_reaper: address) -> uint256:
    return 0


@view
@external
def lastSnapshotTimestamp() -> uint256:
    return 0


@view
@external
def lastSnapshotIndex() -> uint256:
    return 0


@external
def snapshot(_gasToken: address):
    pass


@external
def vote(_reaper: address, _coin: address, _amount: uint256, _gasToken: address):
    pass


@external
def unvote(_reaper: address, _coin: address, _amount: uint256, _gasToken: address):
    pass


@view
@external
def availableToUnvote(_reaper: address, _coin: address, _account: address) -> uint256:
    return 0


@external
def voteIntegral(_reaper: address) -> uint256:
    return 0


@view
@external
def reaperVotePower(_reaper: address) -> uint256:
    return 0


@view
@external
def accountVotePower(_reaper: address, _account: address) -> uint256:
    return 0


@view
@external
def totalVotePower() -> uint256:
    return 0


@external
def startVoting(_votingDelay: uint256 = 0):
    pass
