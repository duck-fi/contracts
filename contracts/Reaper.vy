# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Reaper as Reaper
import interfaces.ReaperController as ReaperController
import interfaces.Ownable as Ownable
import interfaces.VotingController as VotingController
import interfaces.Minter as Minter
import interfaces.tokens.Farmable as Farmable
import interfaces.strategies.ReaperStrategy as ReaperStrategy


implements: Reaper
implements: Ownable


event Deposit:
    provider: indexed(address)
    value: uint256

event Withdraw:
    provider: indexed(address)
    value: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MULTIPLIER: constant(uint256) = 10 ** 18


lp_token: public(address)
controller: public(address)
voting_controller: public(address)
strategy: public(address)

allowance: public(HashMap[address, HashMap[address, bool]])
balanceOf: public(HashMap[address, uint256])
totalSupply: public(uint256)

farm_integral_for: public(HashMap[address, uint256])
farm_total_supply_integral: public(uint256)
last_snapshot_block: public(uint256)
unit_cost_integral: public(uint256)
unit_cost_integral_for: public(HashMap[address, uint256])
last_rate_integral: public(uint256)
last_vote_integral: public(uint256)

owner: public(address)
future_owner: public(address)

is_killed: bool


@external
def __init__(_lp_token: address, _controller: address, _strategy: address, _voting_controller: address):
    self.lp_token = _lp_token
    self.controller = _controller
    self.voting_controller = _voting_controller
    self.strategy = _strategy


@external
def approve(account: address, can_deposit: bool):
    self.allowance[account][msg.sender] = can_deposit


@internal
def _snapshot(account: address):
    assert not self.is_killed, "reaper is dead"

    farm_token: address = Minter(ReaperController(self.controller).minter()).token()
    rate_integral: uint256 = Farmable(farm_token).rateIntegral()
    vote_integral: uint256 = VotingController(self.voting_controller).reaper_integrated_votes(self)

    new_unit_cost_integral: uint256 = self.unit_cost_integral + (rate_integral - self.last_rate_integral) * (vote_integral - self.last_vote_integral) / self.totalSupply
    self.last_rate_integral = rate_integral
    self.last_vote_integral = vote_integral

    self.farm_integral_for[account] += self.balanceOf[account] * (new_unit_cost_integral - self.unit_cost_integral_for[account]) / MULTIPLIER
    self.farm_total_supply_integral +=  new_unit_cost_integral * self.totalSupply
    self.unit_cost_integral_for[account] = new_unit_cost_integral
    self.unit_cost_integral = new_unit_cost_integral


@external
def deposit(amount: uint256, account: address = msg.sender):
    if account != msg.sender:
        assert self.allowance[msg.sender][account], "Not approved"

    self._snapshot(account)

    if amount != 0:
        ERC20(self.lp_token).transferFrom(msg.sender, self, amount)
        deltaBalance: uint256 = amount

        if self.strategy != ZERO_ADDRESS:
            deltaBalance = ReaperStrategy(self.strategy).deposit(amount, account)
        
        self.balanceOf[account] += deltaBalance
        self.totalSupply += deltaBalance
        
        log Deposit(account, deltaBalance)


@external
def withdraw(amount: uint256):
    self._snapshot(msg.sender)

    withdraw_amount: uint256 = ReaperStrategy(self.strategy).withdraw(amount, msg.sender)
    ERC20(self.lp_token).transfer(msg.sender, withdraw_amount)
    
    self.balanceOf[msg.sender] -= amount
    self.totalSupply -= amount
    log Withdraw(msg.sender, amount)


@external
def snapshot(account: address):
    self._snapshot(account)


@external
def kill():
    assert msg.sender == self.owner, "owner only"
    self.is_killed = True


@external
def setStrategy(_strategy: address):
    assert msg.sender == self.owner, "owner only"
    ERC20(self.lp_token).approve(_strategy, MAX_UINT256)
    self.strategy = _strategy


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
