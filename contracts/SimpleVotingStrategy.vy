# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.strategies.VotingStrategy as VotingStrategy


implements: VotingStrategy


owner: public(address)
coin: public(address)
coinVoteRatio: public(uint256)
unlocked_coins: public(HashMap[address, uint256])
locked_coins: public(HashMap[address, uint256])
last_modified_block: public(HashMap[address, uint256])
blockPeriod: public(uint256)


@external
def __init__(_coin: address):
    self.coin = _coin
    self.owner = msg.sender


@view
@external
def coinToVotes(_amount: uint256) -> uint256: 
    return _amount * self.coinVoteRatio


@view
@external
def availableToUnvote(_account: address, _amount: uint256) -> uint256:
    if block.timestamp > self.last_modified_block[_account] + self.blockPeriod:
        return self.locked_coins[_account]+self.unlocked_coins[_account]

    return self.unlocked_coins[_account]


@external
@nonreentrant('lock')
def vote(_account: address, _amount: uint256) -> uint256: 
    if block.timestamp > self.last_modified_block[_account] + self.blockPeriod and self.locked_coins[_account] > 0:
        self.unlocked_coins[_account] += self.locked_coins[_account]
        self.locked_coins[_account] = 0

    self.locked_coins[_account] += _amount
    self.last_modified_block[_account] = block.timestamp
    
    return _amount


@external
@nonreentrant('lock')
def unvote(_account: address, _amount: uint256) -> uint256: 
    assert self.unlocked_coins[_account] + self.locked_coins[_account] >= _amount, "insufficient funds"
    
    if block.timestamp > self.last_modified_block[_account] + self.blockPeriod and self.locked_coins[_account] > 0:
        self.unlocked_coins[_account] += self.locked_coins[_account]
        self.locked_coins[_account] = 0

    assert self.unlocked_coins[_account] >= _amount, "funds are locked"
    self.unlocked_coins[_account] -= _amount

    return _amount