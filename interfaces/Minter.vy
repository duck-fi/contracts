# @version ^0.2.0


@external
def mintFor(_reaper: address, _account: address): 
    pass


@view
@external
def minted(_reaper: address, _account: address) -> uint256:
    return 0


@view
@external
def mintAllowance(_reaper: address, _owner: address, _minter: address) -> bool:
    return False


@external
def mintApprove(_reaper: address, _minter: address, _canMint: bool):
    pass