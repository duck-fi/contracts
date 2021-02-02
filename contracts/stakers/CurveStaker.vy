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


implements: Staker
implements: Ownable


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


reaperStrategy: public(address)
stakeToken: public(address)
rewardToken: public(address)
stakeContract: public(address)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_stakeContract: address, _stakeToken: address, _rewardToken: address):
    assert _stakeToken != ZERO_ADDRESS, "StakeToken param is required"
    assert _rewardToken != ZERO_ADDRESS, "RewardToken param is required"
    assert _stakeContract != ZERO_ADDRESS, "StakeContract param is required"
    self.stakeToken = _stakeToken
    self.rewardToken = _rewardToken
    self.stakeContract = _stakeContract
    self.owner = msg.sender


@external
def setReaperStrategy(_reaperStrategy: address):
    assert msg.sender == self.owner, "owner only"
    assert _reaperStrategy != ZERO_ADDRESS
    self.reaperStrategy = _reaperStrategy


@external
def stake(_amount: uint256):
    assert msg.sender == self.reaperStrategy , "reaperStrategy only"
    LiquidityGauge(self.stakeContract).deposit(_amount)


@external
def unstake(_amount: uint256, _recipient: address = msg.sender):
    _reaperStrategy: address = self.reaperStrategy
    assert msg.sender == _reaperStrategy, "reaperStrategy only"
    LiquidityGauge(self.stakeContract).withdraw(_amount)
    ERC20(self.stakeToken).transfer(_recipient, _amount)


@external
def claim(_recipient: address = msg.sender) -> uint256: 
    _reaperStrategy: address = self.reaperStrategy
    _stakeContract: address = self.stakeContract
    assert msg.sender == _reaperStrategy, "reaperStrategy only"
    
    claimableTokens: uint256 = LiquidityGauge(_stakeContract).claimable_tokens(self)
    if claimableTokens > 0:
        Minter(LiquidityGauge(_stakeContract).minter()).mint(_stakeContract)
        ERC20(self.rewardToken).transfer(_recipient, claimableTokens)

    return claimableTokens


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
