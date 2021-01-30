# @version ^0.2.0


import interfaces.Controller as Controller
import interfaces.Minter as Minter
import interfaces.Ownable as Ownable
import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Reaper as Reaper


implements: Minter
implements: Ownable
implements: Controller


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


MAX_REAPERS_COUNT: constant(uint256) = 10 ** 6


farmToken: public(address)
reapers: public(address[MAX_REAPERS_COUNT])
lastReaperIndex: public(uint256)
indexByReaper: public(HashMap[address, uint256])
minted: public(HashMap[address, HashMap[address, uint256]])
mintAllowance: public(HashMap[address, HashMap[address, HashMap[address, bool]]])

owner: public(address)
futureOwner: public(address)


@external
def __init__(_farmToken: address):
    self.farmToken = _farmToken
    self.owner = msg.sender


@external
@nonreentrant('lock')
def mintFor(_reaper: address, _account: address = msg.sender):
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"

    if _account != msg.sender:
        assert self.mintAllowance[_reaper][_account][msg.sender], "mint is not allowed"

    Reaper(_reaper).snapshot(_account)
    totalMinted: uint256 = Reaper(_reaper).reapIntegralFor(_account)
    toMint: uint256 = totalMinted - self.minted[_reaper][_account]

    if toMint != 0:
        ERC20Mintable(self.farmToken).mint(_account, toMint)
        self.minted[_reaper][_account] = totalMinted


@external
def mintableTokens(_reaper: address, _account: address) -> uint256:
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"
    Reaper(_reaper).snapshot(_account)
    return Reaper(_reaper).reapIntegralFor(_account) - self.minted[_reaper][_account]


@external
def mintApprove(_reaper: address, _minter: address, _canMint: bool):
    self.mintAllowance[_reaper][msg.sender][_minter] = _canMint


@external
def addReaper(_reaper: address):
    assert msg.sender == self.owner, "owner only"
    assert _reaper != ZERO_ADDRESS
    reaperIndex: uint256 = self.indexByReaper[_reaper]
    assert reaperIndex == 0, "reaper is exist"

    reaperIndex = self.lastReaperIndex + 1
    self.reapers[reaperIndex] = _reaper
    self.indexByReaper[_reaper] = reaperIndex
    self.lastReaperIndex = reaperIndex


@external
def removeReaper(_reaper: address):
    assert msg.sender == self.owner, "owner only"
    reaperIndex: uint256 = self.indexByReaper[_reaper]
    assert reaperIndex > 0, "reaper is not exist"

    recentReaperIndex: uint256 = self.lastReaperIndex
    lastReaper: address = self.reapers[recentReaperIndex]

    self.reapers[reaperIndex] = lastReaper
    self.indexByReaper[lastReaper] = reaperIndex
    self.indexByReaper[_reaper] = 0
    self.lastReaperIndex = recentReaperIndex - 1


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
