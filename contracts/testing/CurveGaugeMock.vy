# @version ^0.2.11
"""
@title Curve Gauge Mock
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.Staker as Staker


interface Minter:
    def minted(_account: address, _gauge: address) -> uint256: view


minter: public(address)
stakeToken: public(address)
rewardToken: public(address)
balances: public(HashMap[address, uint256])
totalBalances: public(uint256)

reapIntegral: public(uint256)
reapIntegralFor: public(HashMap[address, uint256])
lastReapTimestamp: public(uint256)
lastReapTimestampFor: public(HashMap[address, uint256])


@external
def __init__(_minter: address, _stakeToken: address, _rewardToken: address):
    assert _minter != ZERO_ADDRESS
    assert _stakeToken != ZERO_ADDRESS
    assert _rewardToken != ZERO_ADDRESS
    self.minter = _minter
    self.stakeToken = _stakeToken
    self.rewardToken = _rewardToken


@internal
def _snapshot(_account: address):
    if self.lastReapTimestamp > 0:
        self.reapIntegral = self.reapIntegral + self.totalBalances * (block.timestamp - self.lastReapTimestamp)
    
    if self.lastReapTimestampFor[_account] > 0:
        self.reapIntegralFor[_account] = self.reapIntegralFor[_account] + self.balances[_account] * (block.timestamp - self.lastReapTimestampFor[_account])
    
    self.lastReapTimestamp = block.timestamp
    self.lastReapTimestampFor[_account] = block.timestamp


@external
@nonreentrant('lock')
def deposit(_amount: uint256):
    self._snapshot(msg.sender)
    self.totalBalances += _amount
    self.balances[msg.sender] += _amount
    assert ERC20(self.stakeToken).transferFrom(msg.sender, self, _amount)


@external
@nonreentrant('lock')
def withdraw(_amount: uint256):
    self._snapshot(msg.sender)
    self.balances[msg.sender] -= _amount
    self.totalBalances -= _amount
    assert ERC20(self.stakeToken).transfer(msg.sender, _amount)


@external
def claimable_tokens(_account: address) -> uint256:
    self._snapshot(_account)
    
    return self.reapIntegralFor[_account] - Minter(self.minter).minted(_account, self)


@external
def snapshot(_account: address):
    self._snapshot(_account)
