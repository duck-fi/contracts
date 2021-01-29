# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.tokens.ERC20Detailed as ERC20Detailed
import interfaces.tokens.ERC20Burnable as ERC20Burnable
import interfaces.tokens.ERC20Mintable as ERC20Mintable
import interfaces.Ownable as Ownable
import interfaces.tokens.Farmable as Farmable


implements: ERC20
implements: ERC20Detailed
implements: ERC20Burnable
implements: ERC20Mintable
implements: Farmable
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
    admin: address

event ApplyOwnership:
    admin: address


YEAR: constant(uint256) = 86_400 * 365
INITIAL_EMISSION: constant(uint256) = 1_000_000
EMISSION_REDUCTION_TIME: constant(uint256) = YEAR
EMISSION_REDUCTION_DELIMITER: constant(uint256) = 2


name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)
balanceOf: public(HashMap[address, uint256])
totalSupply: public(uint256)
allowance: public(HashMap[address, HashMap[address, uint256]])

_yearEmission: uint256
_emissionIntegral: uint256
startEmissionTimestamp: public(uint256)
lastEmissionUpdateTimestamp: public(uint256)

minter: public(address)
owner: public(address)
futureOwner: public(address)


@external
def __init__(_name: String[64], _symbol: String[32], _decimals: uint256, _supply: uint256):
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
def setName(_name: String[64], _symbol: String[32]):
    assert msg.sender == self.owner, "owner only"
    self.name = _name
    self.symbol = _symbol


@external
def startEmission():
    assert msg.sender == self.owner, "owner only"
    assert self.lastEmissionUpdateTimestamp == 0, "emission already started"
    self._yearEmission = INITIAL_EMISSION
    self.lastEmissionUpdateTimestamp = block.timestamp
    self.startEmissionTimestamp = block.timestamp


@internal
def _updateYearEmission() -> uint256:
    futureEmissionUpdateTimestamp: uint256 = self.lastEmissionUpdateTimestamp + EMISSION_REDUCTION_TIME
    lastYearEmission: uint256 = self._yearEmission

    if block.timestamp > futureEmissionUpdateTimestamp:
        self._emissionIntegral += EMISSION_REDUCTION_TIME * lastYearEmission
        self.lastEmissionUpdateTimestamp = futureEmissionUpdateTimestamp
        lastYearEmission /= EMISSION_REDUCTION_DELIMITER
        self._yearEmission = lastYearEmission

    return lastYearEmission


@external
def yearEmission() -> uint256:
    return self._updateYearEmission()


@internal
def _currentEmissionIntegral() -> uint256:
    return self._emissionIntegral + self._updateYearEmission() * (block.timestamp - self.lastEmissionUpdateTimestamp) / YEAR


@external
def emissionIntegral() -> uint256:
    return self._currentEmissionIntegral()


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
    assert amount == 0 or self.allowance[msg.sender][_spender] == 0, "already approved"
    self.allowance[msg.sender][_spender] = amount
    log Approval(msg.sender, _spender, amount)
    return True


@external
def setMinter(_minter: address):
    assert msg.sender == self.owner, "owner only"
    assert _minter != ZERO_ADDRESS
    self.minter = _minter


@external
def mint(account: address, amount: uint256):
    assert msg.sender == self.minter
    assert account != ZERO_ADDRESS

    _totalSupply: uint256 = self.totalSupply
    self.totalSupply = _totalSupply + amount
    self.balanceOf[account] += amount
    assert self._currentEmissionIntegral() / (block.timestamp - self.startEmissionTimestamp) >= _totalSupply + amount, "exceeds allowable mint amount"

    log Transfer(ZERO_ADDRESS, account, amount)


@external
def burn(amount: uint256):
    self.totalSupply -= amount
    self.balanceOf[msg.sender] -= amount
    log Transfer(msg.sender, ZERO_ADDRESS, amount)


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
