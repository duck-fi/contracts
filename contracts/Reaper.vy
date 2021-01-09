# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Reaper as Reaper
import interfaces.ReaperStrategy as ReaperStrategy
import interfaces.Ownable as Ownable


implements: Reaper
implements: Ownable


event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


base_token: public(address)
controller: public(address)
voting_controller: public(address)
strategy: public(address)
balances: public(HashMap[address, uint256])
total_balance: public(uint256)
farmIntegral: public(HashMap[address, uint256])

owner: public(address)
future_owner: public(address)

is_killed: bool


@external
def __init__(_base_token: address, _controller: address, _strategy: address, _voting_controller: address):
    self.base_token = _base_token
    self.controller = _controller
    self.voting_controller = _voting_controller
    self.strategy = _strategy


@external
def deposit(amount: uint256, account: address = msg.sender):
    assert amount > 0, "amount <= 0"
    ERC20(self.base_token).transferFrom(msg.sender, self, amount)
    self.balances[account] += amount
    ReaperStrategy(self.strategy).deposit(amount, account)
    # ToDo ADD FRACTION LOGIC


@external
def withdraw(amount: uint256):
    assert amount > 0, "amount <= 0"
    ReaperStrategy(self.strategy).withdraw(amount, msg.sender)
    old_balance: uint256 = self.balances[msg.sender]
    assert old_balance >= amount, "amount <= balance"
    ERC20(self.base_token).transfer(msg.sender, amount)
    self.balances[msg.sender] -= amount
    # ToDo ADD FRACTION LOGIC


@external
def checkpoint(account: address):
    pass


@external
def kill():
    assert msg.sender == self.owner, "owner only"
    self.is_killed = True


@external
def setStrategy(_strategy: address):
    assert msg.sender == self.owner, "owner only"
    self.strategy = _strategy


@external
def updateBalance(account: address, amount: uint256):
    assert msg.sender == self.strategy, "strategy only"
    self.total_balance -= amount - self.balances[account]
    self.balances[account] = amount


@external
def setVotingController(_voting_controller: address):
    assert msg.sender == self.owner, "owner only"
    self.voting_controller = _voting_controller


@external
def setController(_controller: address):
    assert msg.sender == self.owner, "owner only"
    self.controller = _controller


@external
def transferOwnership(_future_owner: address):
    assert msg.sender == self.owner, "owner only"

    self.future_owner = _future_owner
    log CommitOwnership(_future_owner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.future_owner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)