# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.tokens.ERC20Mintable as Mintable
import interfaces.tokens.ERC20Burnable as Burnable
import interfaces.tokens.ERC20Detailed as Detailed
import interfaces.tokens.Farmable as Farmable


implements: ERC20
implements: Burnable
implements: Mintable
implements: Detailed
implements: Ownable
implements: Farmable


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


YEAR: constant(uint256) = 86_400 * 365
INITIAL_RATE: constant(uint256) = 274_815_283 * 10 ** 18 / YEAR
RATE_REDUCTION_TIME: constant(uint256) = YEAR
INFLATION_DELAY: constant(uint256) = 86_400 * 7


name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)
balanceOf: public(HashMap[address, uint256])
totalSupply: public(uint256)
allowance: public(HashMap[address, HashMap[address, uint256]])

inflation_rate_by_block: public(uint256)
inflation_rate_integral: public(uint256)
last_rate_timestamp: public(uint256)

minter: public(address)
owner: public(address)
future_owner: public(address)


@external
def __init__(_name: String[32], _symbol: String[4], _decimals: uint256, _supply: uint256):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals

    init_supply: uint256 = _supply * 10 ** _decimals
    self.balanceOf[msg.sender] = init_supply
    self.totalSupply = init_supply
    self.minter = msg.sender
    self.owner = msg.sender

    log Transfer(ZERO_ADDRESS, msg.sender, init_supply)


@external
def startInflation():
    assert msg.sender == self.owner
    if self.last_rate_timestamp == 0:
        self.inflation_rate_by_block = INITIAL_RATE
        self.last_rate_timestamp = block.timestamp


@internal
def _update_rate() -> uint256:
    future_rate_timestamp: uint256 = self.last_rate_timestamp + RATE_REDUCTION_TIME
    last_rate_by_block: uint256 = self.inflation_rate_by_block

    if future_rate_timestamp > block.timestamp:
        self.inflation_rate_integral += RATE_REDUCTION_TIME * last_rate_by_block
        self.last_rate_timestamp = future_rate_timestamp
        last_rate_by_block = last_rate_by_block * 3 / 4
        self.inflation_rate_by_block = last_rate_by_block

    return last_rate_by_block


@external
def rate() -> uint256:
    return self._update_rate()


@external
def rateIntegral() -> uint256:
    current_rate: uint256 = self._update_rate()
    return self.inflation_rate_integral + current_rate * (block.timestamp - self.last_rate_timestamp) 


@external
def transfer(_to : address, _value : uint256) -> bool:
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value

    if msg.sender != self.minter:
        _allowance: uint256 = self.allowance[_from][msg.sender]
        if _allowance != MAX_UINT256:
            self.allowance[_from][msg.sender] = _allowance - _value

    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, amount : uint256) -> bool:
    assert amount == 0 or self.allowance[msg.sender][_spender] == 0
    self.allowance[msg.sender][_spender] = amount
    log Approval(msg.sender, _spender, amount)
    return True


@external
def setMinter(_minter: address) -> bool:
    assert msg.sender == self.minter
    self.minter = _minter
    
    return True


@external
def mint(account: address, amount: uint256) -> bool:
    assert msg.sender == self.minter
    assert account != ZERO_ADDRESS

    self.totalSupply += amount
    self.balanceOf[account] += amount
    log Transfer(ZERO_ADDRESS, account, amount)
    
    return True


@external
def burn(amount: uint256) -> bool:
    self.totalSupply -= amount
    self.balanceOf[msg.sender] -= amount
    log Transfer(msg.sender, ZERO_ADDRESS, amount)

    return True


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
