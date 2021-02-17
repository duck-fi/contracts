# @version ^0.2.0


@view
@external
def name() -> String[32]:
    return ""


@view
@external
def symbol() -> String[8]:
    return ""


@view
@external
def decimals() -> uint256:
    return 0


@external
def setName(_name: String[32], _symbol: String[8]):
    pass
