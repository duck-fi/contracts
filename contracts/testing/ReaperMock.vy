# @version ^0.2.0

from vyper.interfaces import ERC20


lpToken: public(address)
farmToken: public(address)
reapIntegral: public(uint256)
lastReapTimestamp: public(uint256)
reapIntegralFor: public(HashMap[address, uint256])
lastReapTimestampFor: public(HashMap[address, uint256])
balances: public(HashMap[address, uint256])
totalBalances: public(uint256)


@external
def __init__(_lpToken: address, _farmToken: address):
    assert _lpToken != ZERO_ADDRESS, "_lpToken is not set"
    assert _farmToken != ZERO_ADDRESS, "_farmToken is not set"
    self.lpToken = _lpToken
    self.farmToken = _farmToken


@internal
def _snapshot(_account: address):
    if self.lastReapTimestampFor[_account] == 0:
        self.lastReapTimestampFor[_account] = block.timestamp

        if self.lastReapTimestamp == 0:
            self.lastReapTimestamp = block.timestamp
        
        return

    self.reapIntegralFor[_account] = self.reapIntegralFor[_account] + self.balances[_account] * (block.timestamp - self.lastReapTimestampFor[_account])
    self.reapIntegral = self.reapIntegral + self.totalBalances * (block.timestamp - self.lastReapTimestamp)
    self.lastReapTimestampFor[_account] = block.timestamp
    self.lastReapTimestamp = block.timestamp


@external
def snapshot(_account: address, _gasToken: address = ZERO_ADDRESS):
    self._snapshot(_account)


@external
def deposit(_amount: uint256):
    self._snapshot(msg.sender)
    self.totalBalances += _amount
    self.balances[msg.sender] += _amount
    assert ERC20(self.lpToken).transferFrom(msg.sender, self, _amount)


@external
def withdraw(_amount: uint256):
    self._snapshot(msg.sender)
    self.balances[msg.sender] -= _amount
    self.totalBalances -= _amount
    assert ERC20(self.lpToken).transfer(msg.sender, _amount)
