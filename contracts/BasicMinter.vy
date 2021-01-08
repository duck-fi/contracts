# @version ^0.2.0


import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Minter as Minter
import interfaces.Reaper as Reaper


implements: Minter


event Minted:
    recipient: indexed(address)
    reaper: address
    minted: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


token: public(address)
reapers: public(HashMap[address, bool])
minted: public(HashMap[address, HashMap[address, uint256]])
allowance: public(HashMap[address, HashMap[address, bool]])

owner: public(address)
future_owner: public(address)


@external
def __init__(_token: address):
    self.token = _token


@external
def toggleApprove(account: address):
    self.allowance[account][msg.sender] = not self.allowance[account][msg.sender]


@internal
def _mint_for(reaper: address, account: address):
    assert self.reapers[reaper], "reaper is not supported"

    Reaper(reaper).checkpoint(account)
    total_mint: uint256 = Reaper(reaper).farmIntegral(account)
    to_mint: uint256 = total_mint - self.minted[reaper][account]

    if to_mint != 0:
        ERC20Mintable(self.token).mint(account, to_mint)
        self.minted[reaper][account] = total_mint

        log Minted(account, reaper, total_mint)


@external
@nonreentrant('lock')
def mint(reaper: address):
    self._mint_for(reaper, msg.sender)


@external
@nonreentrant('lock')
def mintFor(reaper: address, account: address):
    if self.allowance[msg.sender][account]:
        self._mint_for(reaper, account)



@external
@nonreentrant('lock')
def addReaper(reaper: address):
    assert msg.sender == self.owner, "owner only"
    self.reapers[reaper] = True


@external
@nonreentrant('lock')
def removeReaper(reaper: address):
    assert msg.sender == self.owner, "owner only"
    self.reapers[reaper] = False


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