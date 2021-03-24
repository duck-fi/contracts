# @version ^0.2.11


@view
@external
def reaper() -> address:
    return ZERO_ADDRESS


@view
@external
def lastBalance(_coin: address) -> uint256:
    return 0


@view
@external
def rewardIntegral(_coin: address) -> uint256:
    return 0


@view
@external
def rewardIntegralFor(_coin: address, _account: address) -> uint256:
    return 0


@view
@external
def reapIntegralFor(_coin: address, _account: address) -> uint256:
    return 0


@view
@external
def totalReapIntegralFor(_coin: address, _account: address) -> uint256:
    return 0


@view
@external
def claimAllowance(_coin: address,  _owner: address, _claimer: address) -> bool:
    return False


@external
def claimApprove(_coin: address, _claimer: address, _canClaim: bool):
    pass


@external
def claim(_coin: address, _account: address, _gasToken: address):
    pass


@view
@external
def claimableTokens(_coin: address, _account: address) -> uint256:
    return 0


@external
def emergencyWithdraw(_coin: address):
    pass


@external
def claimAdminFee(_coin: address, _gasToken: address):
    pass
