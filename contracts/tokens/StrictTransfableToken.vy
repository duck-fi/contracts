# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.tokens.ERC20Detailed as ERC20Detailed
import interfaces.tokens.ERC20Burnable as ERC20Burnable
import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Ownable as Ownable
import interfaces.AddressesCheckList as AddressesCheckList


implements: ERC20
implements: ERC20Detailed
implements: ERC20Burnable
implements: Ownable


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


DECIMALS: constant(uint256) = 18


owner: public(address)
futureOwner: public(address)
mintersCheckList: public(address)
transfableAccount: public(address)

# ERC20
name: public(String[32])
symbol: public(String[8])
balanceOf: public(HashMap[address, uint256])
totalSupply: public(uint256)


@external
def __init__(_name: String[32], _symbol: String[8], _mintersCheckList: address, _transfableAccount: address):
    assert _mintersCheckList != ZERO_ADDRESS, "mintersCheckList is not set"
    assert _transfableAccount != ZERO_ADDRESS, "caller is not set"
    self.name = _name
    self.symbol = _symbol
    self.owner = msg.sender
    self.mintersCheckList = _mintersCheckList
    self.transfableAccount = _transfableAccount


@view
@external
def decimals() -> uint256:
    return DECIMALS


@external
def setName(_name: String[32], _symbol: String[8]):
    assert msg.sender == self.owner, "owner only"
    self.name = _name
    self.symbol = _symbol


@external
def mint(_account: address, _amount: uint256):
    assert AddressesCheckList(self.mintersCheckList).get(msg.sender), "minter only"
    assert _account != ZERO_ADDRESS, "zero address"
    self.totalSupply += _amount
    self.balanceOf[_account] += _amount
    log Transfer(ZERO_ADDRESS, _account, _amount)


@external
def transfer(_recipient: address, _amount: uint256) -> bool:
    assert _recipient != ZERO_ADDRESS, "recipient is zero address"
    assert (msg.sender == self.transfableAccount) or (_recipient == self.transfableAccount), "strict transfer"

    self.balanceOf[msg.sender] -= _amount
    self.balanceOf[_recipient] += _amount
    log Transfer(msg.sender, _recipient, _amount)
    return True


@external
def transferFrom(_sender: address, _recipient: address, _amount: uint256) -> bool:
    assert _sender != ZERO_ADDRESS, "sender is zero address"
    assert _recipient != ZERO_ADDRESS, "recipient is zero address"
    assert msg.sender == self.transfableAccount, "strict transfer"
    
    self.balanceOf[_sender] -= _amount
    self.balanceOf[_recipient] += _amount

    log Transfer(_sender, _recipient, _amount)
    return True


@external
def approve(_spender: address, _amount: uint256) -> bool:
    return False


@view
@external
def allowance(_sender: address, _recipient: address) -> uint256: 
    return 0


@external
def burn(_amount: uint256):
    self.totalSupply -= _amount
    self.balanceOf[msg.sender] -= _amount
    log Transfer(msg.sender, ZERO_ADDRESS, _amount)


@external
def transferOwnership(_futureOwner: address):
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
