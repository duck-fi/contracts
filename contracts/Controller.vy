# @version ^0.2.0


import interfaces.Controller as Controller
import interfaces.Minter as Minter
import interfaces.Ownable as Ownable
import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Reaper as Reaper
import interfaces.GasToken as GasToken
import interfaces.GasReducible as GasReducible


implements: Minter
implements: Ownable
implements: Controller
implements: GasReducible


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
gasTokens: public(HashMap[address, bool])

owner: public(address)
futureOwner: public(address)


@external
def __init__(_farmToken: address):
    assert _farmToken != ZERO_ADDRESS, "_farmToken is not set"
    self.farmToken = _farmToken
    self.owner = msg.sender


@external
@nonreentrant('lock')
def mintFor(_reaper: address, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"
    assert _gasToken == ZERO_ADDRESS or self.gasTokens[_gasToken], "unsupported gas token"

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.mintAllowance[_reaper][_account][msg.sender], "mint is not allowed"

    Reaper(_reaper).snapshot(_account, ZERO_ADDRESS)
    totalMinted: uint256 = Reaper(_reaper).reapIntegralFor(_account)
    toMint: uint256 = totalMinted - self.minted[_reaper][_account]

    if toMint != 0:
        ERC20Mintable(self.farmToken).mint(_account, toMint)
        self.minted[_reaper][_account] = totalMinted
    
    if _gasToken != ZERO_ADDRESS:
        gasSpent: uint256 = 21000 + _gasStart - msg.gas + 16 * (4 + 32 * 3)
        GasToken(_gasToken).freeFromUpTo(msg.sender, (gasSpent + 14154) / 41130)


@external
def mintableTokens(_reaper: address, _account: address) -> uint256:
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"
    Reaper(_reaper).snapshot(_account, ZERO_ADDRESS)
    return Reaper(_reaper).reapIntegralFor(_account) - self.minted[_reaper][_account]


@external
def mintApprove(_reaper: address, _minter: address, _canMint: bool):
    self.mintAllowance[_reaper][msg.sender][_minter] = _canMint


@external
def setGasToken(_gasToken: address, _value: bool):
    assert msg.sender == self.owner, "owner only"
    assert _gasToken != ZERO_ADDRESS, "_gasToken is not set"
    
    self.gasTokens[_gasToken] = _value


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
def claimAdminFee(_reaper: address, _gasToken: address = ZERO_ADDRESS):
    assert msg.sender == self.owner, "owner only"
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"
    assert _gasToken == ZERO_ADDRESS or self.gasTokens[_gasToken], "unsupported gas token"

    _gasStart: uint256 = msg.gas

    Reaper(_reaper).snapshot(_reaper, ZERO_ADDRESS)
    totalMinted: uint256 = Reaper(_reaper).reapIntegralFor(_reaper)
    toMint: uint256 = totalMinted - self.minted[_reaper][_reaper]

    if toMint != 0:
        ERC20Mintable(self.farmToken).mint(msg.sender, toMint)
        self.minted[_reaper][_reaper] = totalMinted

    if _gasToken != ZERO_ADDRESS:
        gasSpent: uint256 = 21000 + _gasStart - msg.gas + 16 * (4 + 32 * 2)
        GasToken(_gasToken).freeFromUpTo(msg.sender, (gasSpent + 14154) / 41130)


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
