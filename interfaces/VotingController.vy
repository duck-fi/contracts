# @version ^0.2.0


@view
@external
def controller() -> address:
    return ZERO_ADDRESS


@view
@external
def coins(_index: uint256) -> address:
    return ZERO_ADDRESS


@view
@external
def lastCoinIndex() -> uint256:
    return 0


@view
@external
def indexByCoin(_coin: address) -> uint256:
    return 0


@view
@external
def strategyByCoin(_coin: address) -> address:
    return ZERO_ADDRESS


@view
@external
def balances(_reaper: address, _coin: address, _account: address) -> uint256:
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
def votingPeriod() -> uint256:
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


@view
@external
def voteAllowance(_reaper: address, _coin: address, _owner: address, _voter: address) -> bool:
    return False


@external
def snapshot():
    pass


@external
def vote(_reaper: address, _coin: address, _amount: uint256, _account: address):
    pass


@external
def unvote(_reaper: address, _coin: address, _amount: uint256, _account: address):
    pass


@view
@external
def availableToUnvote(_reaper: address, _coin: address, _account: address) -> uint256:
    return 0


@view
@external
def reaperVotePower(_reaper: address) -> uint256:
    return 0


@view
@external
def accountVotePower(_reaper: address, _coin: address, _account: address) -> uint256:
    return 0


@external
def voteApprove(_reaper: address, _coin: address, _voter: address, _canVote: bool):
    pass


@external
def setVoteStrategy(_coin: address, _voteStrategy: address):
    pass


@external
def setVotingPeriod(_votingPeriod: uint256):
    pass