# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.tokens.mintable as Mintable
import interfaces.tokens.burnable as Burnable


implements: ERC20
implements: Burnable
implements: Mintable


event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _value: uint256

event Approval:
    _owner: indexed(address)
    _spender: indexed(address)
    _value: uint256


name: public(String[32])
symbol: public(String[4])
decimals: public(uint256)

balanceOf: public(HashMap[address, uint256])
allowances: HashMap[address, HashMap[address, uint256]]
total_supply: uint256
supply_controller: public(address)


@external
def __init__(_name: String[32], _symbol: String[4], _decimals: uint256, _supply: uint256):
    init_supply: uint256 = _supply * 10 ** _decimals
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balanceOf[msg.sender] = init_supply
    self.total_supply = init_supply
    self.supply_controller = msg.sender
    log Transfer(ZERO_ADDRESS, msg.sender, init_supply)


@view
@external
def totalSupply() -> uint256:
    return self.total_supply


@view
@external
def allowance(_owner : address, _spender : address) -> uint256:
    return self.allowances[_owner][_spender]


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

    if msg.sender != self.supply_controller:
        _allowance: uint256 = self.allowances[_from][msg.sender]
        if _allowance != MAX_UINT256:
            self.allowances[_from][msg.sender] = _allowance - _value

    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    assert _value == 0 or self.allowances[msg.sender][_spender] == 0
    self.allowances[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def mint(account: address, amount: uint256) -> bool:
    assert msg.sender == self.supply_controller
    assert account != ZERO_ADDRESS

    self.total_supply += amount
    self.balanceOf[account] += amount
    log Transfer(ZERO_ADDRESS, account, amount)
    
    return True


@external
def burn(amount: uint256) -> bool:
    self.total_supply -= amount
    self.balanceOf[msg.sender] -= amount
    log Transfer(msg.sender, ZERO_ADDRESS, amount)

    return True


@external
def burnFrom(account: address, amount: uint256) -> bool:
    assert msg.sender == self.supply_controller
    assert account != ZERO_ADDRESS

    self.total_supply -= amount
    self.balanceOf[account] -= amount
    log Transfer(account, ZERO_ADDRESS, amount)

    return True