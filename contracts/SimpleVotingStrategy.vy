# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.strategies.VotingStrategy as VotingStrategy


implements: VotingStrategy


owner: public(address)
coin: public(address)
coin_vote_ratio: public(uint256)
unlocked_coins: public(HashMap[address, uint256])
locked_coins: public(HashMap[address, uint256])
last_modified_block: public(HashMap[address, uint256])
lock_period: public(uint256)


@external
def __init__(_coin: address, _coin_vote_ratio: uint256, _lock_period: uint256):
    self.coin = _coin
    self.coin_vote_ratio = _coin_vote_ratio
    self.lock_period = _lock_period
    self.owner = msg.sender


@view
@internal
def _isCoinsReadyToUnlock(_account: address) -> bool:
    # it is better to check locked_coins first to reduce gas
    return self.locked_coins[_account] > 0 and block.timestamp > self.last_modified_block[_account] + self.lock_period


@internal
def _unlockCoinsIfReady(_account: address):
    if self._isCoinsReadyToUnlock(_account):
        self.unlocked_coins[_account] += self.locked_coins[_account]
        self.locked_coins[_account] = 0


@view
@external
def coinToVotes(_amount: uint256) -> uint256: 
    return _amount * self.coin_vote_ratio


@view
@external
def availableToUnvote(_account: address, _amount: uint256) -> uint256:
    additionalToUnlock: uint256 = 0
    if self._isCoinsReadyToUnlock(_account):
        additionalToUnlock = self.locked_coins[_account]

    return self.unlocked_coins[_account] + additionalToUnlock


@external
@nonreentrant('lock')
def vote(_account: address, _amount: uint256) -> uint256: 
    self._unlockCoinsIfReady(_account)

    self.locked_coins[_account] += _amount
    self.last_modified_block[_account] = block.timestamp
    
    return _amount


@external
@nonreentrant('lock')
def unvote(_account: address, _amount: uint256) -> uint256: 
    self._unlockCoinsIfReady(_account)

    assert self.unlocked_coins[_account] >= _amount, "funds are locked"
    self.unlocked_coins[_account] -= _amount

    return _amount


@external
def setLockingPeriod(_lock_period: uint256):
    assert self.owner == msg.sender, "unauthorized"
    assert _lock_period > 0, "invalid params"

    self.lock_period = _lock_period
