# @version ^0.2.0


@view
@external
def reaperStrategy() -> address: 
    return ZERO_ADDRESS


@external
def setReaperStrategy(_reaperStrategy: address): 
    pass


@view
@external
def stakeToken() -> address: 
    return ZERO_ADDRESS


@view
@external
def rewardToken() -> address: 
    return ZERO_ADDRESS


@view
@external
def stakeContract() -> address: 
    return ZERO_ADDRESS


@external
def stake(_amount: uint256): 
    pass


@external
def unstake(_amount: uint256, _recipient: address): 
    pass


@external
def claim(_recipient: address) -> uint256: 
    return 0