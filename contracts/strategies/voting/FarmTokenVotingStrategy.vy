# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.strategies.VotingStrategy as VotingStrategy
import interfaces.Ownable as Ownable


implements: Ownable
implements: VotingStrategy


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


owner: public(address)
futureOwner: public(address)

votingController: public(address)
coin: public(address)
coinVoteRatio: public(uint256)
unlockedCoins: public(HashMap[address, uint256])
lockedCoins: public(HashMap[address, uint256])
lastModifiedAt: public(HashMap[address, uint256])
lockPeriod: public(uint256)


@external
def __init__(_votingController: address, _coin: address, _coinVoteRatio: uint256, _lockPeriod: uint256):
    self.votingController = _votingController
    self.coin = _coin
    self.coinVoteRatio = _coinVoteRatio
    self.lockPeriod = _lockPeriod
    self.owner = msg.sender


@view
@internal
def _isCoinsReadyToUnlock(_account: address) -> bool:
    # it is better to check lockedCoins first to reduce gas
    return self.lockedCoins[_account] > 0 and block.timestamp > self.lastModifiedAt[_account] + self.lockPeriod


@internal
def _unlockCoinsIfReady(_account: address):
    if self._isCoinsReadyToUnlock(_account):
        self.unlockedCoins[_account] += self.lockedCoins[_account]
        self.lockedCoins[_account] = 0


@view
@external
def coinToVotes(_amount: uint256) -> uint256: 
    return _amount * self.coinVoteRatio


@view
@external
def availableToVote(_account: address, _amount: uint256) -> uint256:
    return _amount


@view
@external
def availableToUnvote(_account: address, _amount: uint256) -> uint256:
    additionalToUnlock: uint256 = 0
    if self._isCoinsReadyToUnlock(_account):
        additionalToUnlock = self.lockedCoins[_account]

    return self.unlockedCoins[_account] + additionalToUnlock


@external
@nonreentrant('lock')
def vote(_account: address, _amount: uint256) -> uint256:
    assert self.votingController == msg.sender, "voting controller only"

    self._unlockCoinsIfReady(_account)
    self.lockedCoins[_account] += _amount
    self.lastModifiedAt[_account] = block.timestamp
    
    return _amount


@external
@nonreentrant('lock')
def unvote(_account: address, _amount: uint256) -> uint256:
    assert self.votingController == msg.sender, "voting controller only"

    self._unlockCoinsIfReady(_account)
    assert self.unlockedCoins[_account] >= _amount, "funds are locked"
    self.unlockedCoins[_account] -= _amount

    return _amount


@external
def setLockingPeriod(_lockPeriod: uint256):
    assert self.owner == msg.sender, "owner only"

    self.lockPeriod = _lockPeriod


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
