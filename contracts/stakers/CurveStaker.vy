# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Staker as Staker
import interfaces.Ownable as Ownable


interface Minter:
    def mint(_gauge: address): nonpayable


interface LiquidityGauge:
    def deposit(_value: uint256): nonpayable
    def withdraw(_value: uint256): nonpayable
    def claimable_tokens(addr: address) -> uint256: nonpayable
    def minter() -> address: view


interface VotingEscrow:
    def create_lock(_value: uint256, _unlock_time: uint256): nonpayable
    def increase_amount(_value: uint256): nonpayable
    def withdraw(): nonpayable


implements: Staker
implements: Ownable


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


DAY: constant(uint256) = 86_400
WEEK: constant(uint256) = 7 * DAY
MONTH: constant(uint256) = 30 * DAY
YEAR: constant(uint256) = 365 * DAY


reaperStrategy: public(address)
stakeToken: public(address)
rewardToken: public(address)
stakeContract: public(address)

votingEscrowContract: public(address)
lockedFundsFor: public(HashMap[address, uint256])
lockUntilTimestampFor: public(HashMap[address, uint256])
lockingPeriod: public(uint256)
lockUntilTimestamp: public(uint256)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_stakeContract: address, _stakeToken: address, _rewardToken: address, _votingEscrowContract: address):
    assert _stakeToken != ZERO_ADDRESS, "StakeToken param is required"
    assert _rewardToken != ZERO_ADDRESS, "RewardToken param is required"
    assert _stakeContract != ZERO_ADDRESS, "StakeContract param is required"
    assert _votingEscrowContract != ZERO_ADDRESS, "VotingEscrowContract param is required"
    self.stakeToken = _stakeToken
    self.rewardToken = _rewardToken
    self.stakeContract = _stakeContract
    self.votingEscrowContract = _votingEscrowContract
    self.lockingPeriod = YEAR 

    self.owner = msg.sender


@external
def setLockingPeriod(_lockingPeriod: uint256):
    assert msg.sender == self.owner, "owner only"
    assert MONTH <= _lockingPeriod and _lockingPeriod <= 4 * YEAR, "month <= locking period <= 4 year"
    self.lockingPeriod = _lockingPeriod


@external
def setReaperStrategy(_reaperStrategy: address):
    assert msg.sender == self.owner, "owner only"
    assert _reaperStrategy != ZERO_ADDRESS, "zero address"
    self.reaperStrategy = _reaperStrategy


@external
@nonreentrant('lock')
def stake(_amount: uint256):
    assert msg.sender == self.reaperStrategy , "reaperStrategy only"
    assert ERC20(self.stakeToken).transferFrom(msg.sender, self, _amount)
    LiquidityGauge(self.stakeContract).deposit(_amount)


@external
@nonreentrant('lock')
def unstake(_amount: uint256, _recipient: address = msg.sender):
    _reaperStrategy: address = self.reaperStrategy
    assert msg.sender == _reaperStrategy, "reaperStrategy only"
    LiquidityGauge(self.stakeContract).withdraw(_amount)
    assert ERC20(self.stakeToken).transfer(_recipient, _amount)


@external
@nonreentrant('lock')
def claim(_recipient: address = msg.sender) -> uint256: 
    _reaperStrategy: address = self.reaperStrategy
    _stakeContract: address = self.stakeContract
    assert msg.sender == _reaperStrategy, "reaperStrategy only"
    
    claimableTokens: uint256 = LiquidityGauge(_stakeContract).claimable_tokens(self)
    if claimableTokens > 0:
        Minter(LiquidityGauge(_stakeContract).minter()).mint(_stakeContract)
        ERC20(self.rewardToken).transfer(_recipient, claimableTokens)

    return claimableTokens


@internal
def _depositToEscrow(_crvValue: uint256):
    if block.timestamp > self.lockUntilTimestamp:
        if self.lockUntilTimestamp > 0:
            # finish escrow to start a new one
            VotingEscrow(self.votingEscrowContract).withdraw()
        # start new escrow (round to weeks)
        _lockUntilTimestamp: uint256 = (block.timestamp + self.lockingPeriod) * WEEK / WEEK
        self.lockUntilTimestamp = _lockUntilTimestamp
        VotingEscrow(self.votingEscrowContract).create_lock(_crvValue, _lockUntilTimestamp)
    else:
        # prolongate escrow
        VotingEscrow(self.votingEscrowContract).increase_amount(_crvValue)


@external
@nonreentrant('lock')
def depositToEscrow(_crvValue: uint256, _renewal: bool = False):
    assert _crvValue > 0, "nothing to deposit"
    _lockedFunds: uint256 = self.lockedFundsFor[msg.sender]
    _lockedUntil: uint256 = self.lockUntilTimestampFor[msg.sender]

    if not _renewal:
        assert not (_lockedFunds > 0 and block.timestamp > _lockedUntil), "withdrawal unlocked amount or renewal is needed"
        assert ERC20(self.rewardToken).transferFrom(msg.sender, self, _crvValue)

        self._depositToEscrow(_crvValue)
        self.lockedFundsFor[msg.sender] += _crvValue
        self.lockUntilTimestampFor[msg.sender] = self.lockUntilTimestamp
    else:
        assert _lockedFunds > 0 and block.timestamp > _lockedUntil, "no unlocked amount for renewal"
        assert _crvValue >= _lockedFunds, "withdrawal extra unlocked amount is needed"
        assert ERC20(self.rewardToken).transferFrom(msg.sender, self, _crvValue - _lockedFunds)

        self._depositToEscrow(_crvValue)
        self.lockedFundsFor[msg.sender] = _crvValue
        self.lockUntilTimestampFor[msg.sender] = self.lockUntilTimestamp


@external
@nonreentrant('lock')
def withdrawFromEscrow():
    _lockedFunds: uint256 = self.lockedFundsFor[msg.sender]

    assert _lockedFunds > 0, "nothing to withdraw"
    assert block.timestamp > self.lockUntilTimestampFor[msg.sender], "withdraw is locked"    
    assert ERC20(self.rewardToken).transfer(msg.sender, _lockedFunds), "new lock creation is needed before withdraw"
    
    self.lockedFundsFor[msg.sender] = 0


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
