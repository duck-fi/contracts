# @version ^0.2.0

from vyper.interfaces import ERC20


MAXTIME: constant(uint256) = 4 * 365 * 86400  # 4 years


lockToken: public(address)
lockedAmount: public(HashMap[address, uint256])
lockedUntil: public(HashMap[address, uint256])


@external
def __init__(_lockToken: address):
    assert _lockToken != ZERO_ADDRESS
    self.lockToken = _lockToken
    pass


@external
def create_lock(_amount: uint256, _unlockTime: uint256):
    assert self.lockedAmount[msg.sender] == 0
    assert _unlockTime > block.timestamp
    assert _unlockTime <= block.timestamp + MAXTIME
    
    self.lockedAmount[msg.sender] = _amount
    self.lockedUntil[msg.sender] = _unlockTime

    assert ERC20(self.lockToken).transferFrom(msg.sender, self, _amount)


@external
def increase_amount(_amount: uint256):
    assert _amount > 0
    assert self.lockedAmount[msg.sender] > 0

    self.lockedAmount[msg.sender] += _amount

    assert ERC20(self.lockToken).transferFrom(msg.sender, self, _amount)


@external
def withdraw():
    assert self.lockedAmount[msg.sender] > 0
    assert self.lockedUntil[msg.sender] <= block.timestamp

    _amount: uint256 = self.lockedAmount[msg.sender]
    self.lockedAmount[msg.sender] = 0
    self.lockedUntil[msg.sender] = 0

    assert ERC20(self.lockToken).transfer(msg.sender, _amount)
