# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.tokens.ERC20Mintable as Mintable
import interfaces.tokens.ERC20Burnable as Burnable
import interfaces.tokens.ERC20Detailed as Detailed


implements: ERC20
implements: Burnable
implements: Mintable
implements: Detailed


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256


name: public(String[64])
symbol: public(String[32])
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

    # TODO maybe remove this checks 
    if msg.sender != self.supply_controller:
        _allowance: uint256 = self.allowances[_from][msg.sender]
        if _allowance != MAX_UINT256:
            self.allowances[_from][msg.sender] = _allowance - _value

    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, amount : uint256) -> bool:
    # TODO maybe remove this check
    assert amount == 0 or self.allowances[msg.sender][_spender] == 0
    self.allowances[msg.sender][_spender] = amount
    log Approval(msg.sender, _spender, amount)
    return True


@external
def set_supply_controller(account: address) -> bool:
    assert msg.sender == self.supply_controller
    self.supply_controller = account
    
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

# or maybe burn with allowance
@external
def burnFrom(account: address, amount: uint256) -> bool:
    assert msg.sender == self.supply_controller
    assert account != ZERO_ADDRESS

    self.total_supply -= amount
    self.balanceOf[account] -= amount
    log Transfer(account, ZERO_ADDRESS, amount)

    return True