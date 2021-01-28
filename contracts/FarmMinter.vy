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


token: public(address)
reaperController: public(address)
minted: public(HashMap[address, uint256])

owner: public(address)
futureOwner: public(address)


@external
def __init__(_token: address):
    self.token = _token
    self.owner = msg.sender


@external
@nonreentrant('lock')
def mint(account: address, amount: uint256):
    assert msg.sender == self.reaperController, "reaper controller only"
    ERC20Mintable(self.token).mint(account, amount)
    self.minted[account] += amount


@external
def setReaperController(controller: address):
    assert msg.sender == self.owner, "owner only"
    self.reaperController = controller


@external
def setToken(_token: address):
    assert msg.sender == self.owner, "owner only"
    self.token = _token


@external
def transferOwnership(_futureOwner: address):
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
