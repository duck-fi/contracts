# @version ^0.2.0


import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Minter as Minter
import interfaces.Ownable as Ownable


implements: Minter
implements: Ownable


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


reaper_controller: public(address)
token: public(address)
minted: public(HashMap[address, uint256])

owner: public(address)
future_owner: public(address)


@external
def __init__(_token: address):
    self.token = _token
    self.owner = msg.sender


@external
@nonreentrant('lock')
def mint(account: address, amount: uint256):
    assert msg.sender == self.reaper_controller, "reaper controller only"
    ERC20Mintable(self.token).mint(account, amount)
    self.minted[account] += amount


@external
@nonreentrant('lock')
def setReaperController(controller: address):
    assert msg.sender == self.owner, "owner only"
    self.reaper_controller = controller


@external
@nonreentrant('lock')
def setToken(_token: address):
    assert msg.sender == self.owner, "owner only"
    self.token = _token


@external
def transferOwnership(_future_owner: address):
    assert msg.sender == self.owner, "owner only"

    self.future_owner = _future_owner
    log CommitOwnership(_future_owner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.future_owner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
