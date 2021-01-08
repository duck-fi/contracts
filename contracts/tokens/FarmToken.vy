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
totalSupply: public(uint256)
allowance: public(HashMap[address, HashMap[address, uint256]])
minter: public(address)


@external
def __init__(_name: String[32], _symbol: String[4], _decimals: uint256, _supply: uint256):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals

    init_supply: uint256 = _supply * 10 ** _decimals
    self.balanceOf[msg.sender] = init_supply
    self.totalSupply = init_supply
    self.minter = msg.sender

    log Transfer(ZERO_ADDRESS, msg.sender, init_supply)


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