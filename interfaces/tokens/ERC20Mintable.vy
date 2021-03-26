# @version ^0.2.11


@view
@external
def minter() -> address:
    return ZERO_ADDRESS


@external
def mint(_account: address, _amount: uint256):
    pass


@external
def setMinter(_minter: address):
    pass
