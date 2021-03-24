# @version ^0.2.11
"""
@title Controller
@author Dispersion Finance Team
@license MIT
"""


import interfaces.Controller as Controller
import interfaces.Minter as Minter
import interfaces.Ownable as Ownable
import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Reaper as Reaper
import interfaces.GasToken as GasToken
import interfaces.AddressesCheckList as AddressesCheckList


implements: Minter
implements: Ownable
implements: Controller


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


MAX_REAPERS_COUNT: constant(uint256) = 10 ** 6
MIN_GAS_CONSTANT: constant(uint256) = 21_000


farmToken: public(address)
gasTokenCheckList: public(address)
reapers: public(address[MAX_REAPERS_COUNT])
lastReaperIndex: public(uint256)
indexByReaper: public(HashMap[address, uint256])
minted: public(HashMap[address, HashMap[address, uint256]])
mintAllowance: public(HashMap[address, HashMap[address, HashMap[address, bool]]])
startMintFor: public(bool)

admin: public(address)
owner: public(address)
futureOwner: public(address)


@external
def __init__(_farmToken: address, _gasTokenCheckList: address):
    """
    @notice Contract constructor
    """
    assert _farmToken != ZERO_ADDRESS, "_farmToken is not set"
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"
    self.farmToken = _farmToken
    self.gasTokenCheckList = _gasTokenCheckList
    self.startMintFor = False
    self.owner = msg.sender
    self.admin = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert AddressesCheckList(self.gasTokenCheckList).get(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
@nonreentrant('lock')
def mintFor(_reaper: address, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"
    assert self.startMintFor, "minting is not started yet"

    _gasStart: uint256 = msg.gas
    if _account != msg.sender:
        assert self.mintAllowance[_reaper][_account][msg.sender], "mint is not allowed"

    Reaper(_reaper).snapshot(_account, ZERO_ADDRESS)
    totalMinted: uint256 = Reaper(_reaper).reapIntegralFor(_account)
    toMint: uint256 = totalMinted - self.minted[_reaper][_account]

    if toMint != 0:
        ERC20Mintable(self.farmToken).mint(_account, toMint)
        self.minted[_reaper][_account] = totalMinted
    
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 3)


@external
def mintableTokens(_reaper: address, _account: address) -> uint256:
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"
    Reaper(_reaper).snapshot(_account, ZERO_ADDRESS)
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
@nonreentrant('lock')
def claimAdminFee(_reaper: address, _gasToken: address = ZERO_ADDRESS):
    assert msg.sender == self.admin, "admin only"
    assert self.indexByReaper[_reaper] > 0, "reaper is not supported"

    _gasStart: uint256 = msg.gas
    Reaper(_reaper).snapshot(_reaper, ZERO_ADDRESS)
    totalMinted: uint256 = Reaper(_reaper).reapIntegralFor(_reaper)
    toMint: uint256 = totalMinted - self.minted[_reaper][_reaper]

    if toMint != 0:
        ERC20Mintable(self.farmToken).mint(msg.sender, toMint)
        self.minted[_reaper][_reaper] = totalMinted

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@external
def setAdmin(_admin: address):
    assert msg.sender == self.owner, "owner only"
    assert _admin != ZERO_ADDRESS, "zero address"
    self.admin = _admin


@external
def startMinting():
    assert msg.sender == self.owner, "owner only"
    self.startMintFor = True


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Transfers ownership by setting new owner `_futureOwner` candidate
    @dev Callable by owner only
    @param _futureOwner Future owner address
    """
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies transfer ownership
    @dev Callable by owner only. Function call actually changes owner
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
