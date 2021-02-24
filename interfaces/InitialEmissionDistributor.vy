# @version ^0.2.0


@view
@external
def farmToken() -> address: 
    return ZERO_ADDRESS


@view
@external
def gasTokenCheckList() -> address: 
    return ZERO_ADDRESS


@view
@external
def balances(_account: address) -> uint256:
    return 0


@view
@external
def totalMinted(_account: address) -> uint256:
    return 0


@view
@external
def startClaimingTimestamp() -> uint256:
    return 0


@external
def setBalances(_accounts: address[100], _amounts: uint256[100], _gasToken: address):
    pass


@external
def startClaiming():
    pass


@external
def claim(_account: address, _gasToken: address):
    pass


@view
@external
def claimableTokens(_account: address) -> uint256:
    return 0


@external
def emergencyWithdraw():
    pass