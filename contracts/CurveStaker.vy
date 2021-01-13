# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.StakeInterface as StakeInterface


interface Minter:
    def mint(gauge_addr: address): nonpayable


interface LiquidityGauge:
    def deposit(_value: uint256): nonpayable
    def withdraw(_value: uint256): nonpayable
    def balanceOf(_address: address) -> uint256: view
    def claimable_tokens(addr: address) -> uint256: view
    def lp_token() -> address: view
    def minter() -> address: view
    def crv_token() -> address: view


implements: StakeInterface


owner: public(address)
reaperStrategy: public(address)
curveLiquidityGauge: public(address)


@external
def __init__(_curveLiquidityGauge: address):
    """
    @notice Contract constructor
    """
    assert _curveLiquidityGauge != ZERO_ADDRESS, "LiquidityGauge param is required"

    self.curveLiquidityGauge = _curveLiquidityGauge
    self.owner = msg.sender


@external
def deposit(_amount: uint256):
    assert self.reaperStrategy == msg.sender, "unauthorized"
    assert ERC20(LiquidityGauge(self.curveLiquidityGauge).lp_token()).balanceOf(msg.sender) >= _amount, "insufficiend funds"
    assert ERC20(LiquidityGauge(self.curveLiquidityGauge).lp_token()).transferFrom(msg.sender, self, _amount), "approve required"

    LiquidityGauge(self.curveLiquidityGauge).deposit(_amount)


@external
def withdraw(_amount: uint256, _account: address):
    assert self.reaperStrategy == msg.sender, "unauthorized"
    assert LiquidityGauge(self.curveLiquidityGauge).balanceOf(self) >= _amount, "insufficiend funds"

    LiquidityGauge(self.curveLiquidityGauge).withdraw(_amount)
    ERC20(LiquidityGauge(self.curveLiquidityGauge).lp_token()).transfer(_account, _amount)


@external
def claim():
    assert self.reaperStrategy == msg.sender, "unauthorized" # TODO: or remove it?
    
    claimable_tokens: uint256 = LiquidityGauge(self.curveLiquidityGauge).claimable_tokens(self)
    if claimable_tokens > 0:
        Minter(LiquidityGauge(self.curveLiquidityGauge).minter()).mint(self.curveLiquidityGauge)
        ERC20(LiquidityGauge(self.curveLiquidityGauge).crv_token()).transfer(self.reaperStrategy, claimable_tokens)


@external
def setStrategy(_strategy: address):
    assert self.owner == msg.sender, "unauthorized"
    self.reaperStrategy = _strategy