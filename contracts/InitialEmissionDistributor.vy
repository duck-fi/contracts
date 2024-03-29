# @version ^0.2.11
"""
@title Initial Emission Distributor
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.GasToken as GasToken
import interfaces.WhiteList as WhiteList
import interfaces.InitialEmissionDistributor as InitialEmissionDistributor


implements: Ownable
implements: InitialEmissionDistributor


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address

event StartClaiming:
    ts: uint256

event Claim:
    account: address
    amount: uint256


DAY: constant(uint256) = 86_400
YEAR: constant(uint256) = DAY * 365
MIN_GAS_CONSTANT: constant(uint256) = 21_000
LOCK_PERIOD: constant(uint256) = YEAR


farmToken: public(address)
gasTokenCheckList: public(address)
balances: public(HashMap[address, uint256])
totalMinted: public(HashMap[address, uint256])
startClaimingTimestamp: public(uint256)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_farmToken: address, _gasTokenCheckList: address):
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"
    assert _farmToken != ZERO_ADDRESS, "farmToken is not set"
    self.farmToken = _farmToken
    self.gasTokenCheckList = _gasTokenCheckList
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert WhiteList(self.gasTokenCheckList).check(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
def setBalances(_accounts: address[100], _amounts: uint256[100], _gasToken: address = ZERO_ADDRESS):
    assert msg.sender == self.owner, "owner only"
    _gasStart: uint256 = msg.gas

    assert self.startClaimingTimestamp == 0, "claiming already started"

    for i in range(0, 100):
        if _accounts[i] == ZERO_ADDRESS:
            break
        self.balances[_accounts[i]] = _amounts[i]

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 201)


@external
def startClaiming():
    assert msg.sender == self.owner, "owner only"
    assert self.startClaimingTimestamp == 0, "claiming already started"
    self.startClaimingTimestamp = block.timestamp
    log StartClaiming(block.timestamp)


@external
def claim(_account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    _gasStart: uint256 = msg.gas
    _startClaimingTimestamp: uint256 = self.startClaimingTimestamp
    assert _startClaimingTimestamp > 0, "claiming is not started"

    _totalMinted: uint256 = self.totalMinted[_account]
    dt: uint256 = block.timestamp - _startClaimingTimestamp
    if dt > LOCK_PERIOD: 
        dt = LOCK_PERIOD

    amount: uint256 = dt * self.balances[_account] / LOCK_PERIOD - _totalMinted
    self.totalMinted[_account] = _totalMinted + amount
    assert ERC20(self.farmToken).transfer(_account, amount)
    
    log Claim(_account, amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@view
@external
def claimableTokens(_account: address) -> uint256:
    _startClaimingTimestamp: uint256 = self.startClaimingTimestamp
    if _startClaimingTimestamp == 0:
        return 0

    dt: uint256 = block.timestamp - self.startClaimingTimestamp
    if dt > LOCK_PERIOD: 
        dt = LOCK_PERIOD

    return dt * self.balances[_account] / LOCK_PERIOD - self.totalMinted[_account]


@external
def emergencyWithdraw():
    _owner: address = self.owner
    assert msg.sender == _owner, "owner only"
    _farmToken: address = self.farmToken
    assert ERC20(_farmToken).transfer(_owner, ERC20(_farmToken).balanceOf(self))


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Transfers ownership by setting new owner `_futureOwner` candidate
    @dev Callable by `owner` only. Emit CommitOwnership event with `_futureOwner`
    @param _futureOwner Future owner address
    """
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies transfer ownership
    @dev Callable by `owner` only. Function call actually changes `owner`. 
        Emits ApplyOwnership event with `_owner`
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
