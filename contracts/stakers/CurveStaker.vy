# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Staker as Staker
import interfaces.Ownable as Ownable


interface Minter:
    def mint(_gauge: address): nonpayable


interface LiquidityGauge:
    def deposit(_value: uint256): nonpayable
    def withdraw(_value: uint256): nonpayable
    def claimable_tokens(addr: address) -> uint256: view
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


DAY: constant(uint256) = 86400
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
    assert _lockingPeriod > 0, "invalid param"
    self.lockingPeriod = _lockingPeriod


@external
def setReaperStrategy(_reaperStrategy: address):
    assert msg.sender == self.owner, "owner only"
    assert _reaperStrategy != ZERO_ADDRESS
    self.reaperStrategy = _reaperStrategy


@external
@nonreentrant('lock')
def stake(_amount: uint256):
    assert msg.sender == self.reaperStrategy , "reaperStrategy only"
    LiquidityGauge(self.stakeContract).deposit(_amount)


@external
@nonreentrant('lock')
def unstake(_amount: uint256, _recipient: address = msg.sender):
    _reaperStrategy: address = self.reaperStrategy
    assert msg.sender == _reaperStrategy, "reaperStrategy only"
    LiquidityGauge(self.stakeContract).withdraw(_amount)
    ERC20(self.stakeToken).transfer(_recipient, _amount)


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
        # start new escrow
        _lockUntilTimestamp: uint256 = block.timestamp + self.lockingPeriod
        self.lockUntilTimestamp = _lockUntilTimestamp
        VotingEscrow(self.votingEscrowContract).create_lock(_crvValue, _lockUntilTimestamp)
    else:
        # prolongate escrow
        VotingEscrow(self.votingEscrowContract).increase_amount(_crvValue)


@external
@nonreentrant('lock')
def depositToEscrow(_crvValue: uint256, _renewal: bool = False):
    assert not (self.lockedFundsFor[msg.sender] > 0 and block.timestamp > self.lockUntilTimestampFor[msg.sender] and not _renewal), "withdrawal unlocked amount or renewal is needed"

    if self.lockedFundsFor[msg.sender] > 0 and block.timestamp > self.lockUntilTimestampFor[msg.sender] and _renewal:
        if _crvValue >= self.lockedFundsFor[msg.sender]:
            assert ERC20(self.rewardToken).transferFrom(msg.sender, self, _crvValue - self.lockedFundsFor[msg.sender])
            self._depositToEscrow(_crvValue)
            self.lockedFundsFor[msg.sender] = _crvValue
            self.lockUntilTimestampFor[msg.sender] = self.lockUntilTimestamp
        else: 
            raise "withdrawal unlocked amount is needed"
    else:
        assert ERC20(self.rewardToken).transferFrom(msg.sender, self, _crvValue)
        self._depositToEscrow(_crvValue)
        self.lockedFundsFor[msg.sender] += _crvValue
        self.lockUntilTimestampFor[msg.sender] = self.lockUntilTimestamp


@external
@nonreentrant('lock')
def withdrawFromEscrow():
    assert self.lockedFundsFor[msg.sender] > 0, "nothing to withdraw"
    assert block.timestamp > self.lockUntilTimestampFor[msg.sender], "withdraw is locked"
    assert ERC20(self.rewardToken).balanceOf(self) >= self.lockedFundsFor[msg.sender], "new lock creation is needed"
    
    ERC20(self.rewardToken).transfer(msg.sender, self.lockedFundsFor[msg.sender])
    self.lockedFundsFor[msg.sender] = 0


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
