# @version ^0.2.11


@view
@external
def owner() -> address:
    return ZERO_ADDRESS


@view
@external
def futureOwner() -> address:
    return ZERO_ADDRESS


@external
def transferOwnership(_futureOwner: address):
    pass


@external
def applyOwnership():
    pass
