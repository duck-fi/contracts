# @version ^0.2.11
"""
@title Strict Transferable Token
@author Dispersion Finance Team
@license MIT
@notice Burnable and Mintable ERC20 token.
@dev Based on the [ERC-20](https://eips.ethereum.org/EIPS/eip-20) token that cannot be freely transferred.
     Transfer awailable for `_transfableAccount only`. `decimals()` = `18`.
"""


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
    """
    @notice Contract constructor.
    @dev `owner` = `msg.sender`
    @param _name Token full name
    @param _symbol Token symbol
    @param _mintersCheckList Minters check list. List of addresses that are allowed to mint coins
    @param _transfableAccount Account address with which transfer is allowed
    """
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
    """
    @notice Returns token decimals value.
    @dev For ERC20 compatibility.
    @return Token decimals
    """
    return DECIMALS


@external
def setName(_name: String[32], _symbol: String[8]):
    """
    @notice Changes token name and symbol to `_name` and `_symbol`.
    @dev Callable by `owner` only.
    @param _name New token name
    @param _symbol New token symbol
    """
    assert msg.sender == self.owner, "owner only"
    self.name = _name
    self.symbol = _symbol


@external
def mint(_account: address, _amount: uint256):
    """
    @notice Mints new tokens for account `_account` with amount `_amount`.
    @dev Callable by `minter` only. Emits a `Transfer` event originating from `ZERO_ADDRESS`. 
        `_account` can't be equal `ZERO_ADDRESS`.
    @param _account Account to mint tokens for
    @param _amount Amount to mint
    """
    assert AddressesCheckList(self.mintersCheckList).get(msg.sender), "minter only"
    assert _account != ZERO_ADDRESS, "zero address"
    self.totalSupply += _amount
    self.balanceOf[_account] += _amount
    log Transfer(ZERO_ADDRESS, _account, _amount)


@external
def transfer(_recipient: address, _amount: uint256) -> bool:
    """
    @notice Transfers `_amount` of tokens from `msg.sender` to `_recipient` address
    @dev ERC20 function. Emits a `Transfer` event with `msg.sender`, `_recipient`, `_amount`. 
        `_recipient` can't be equal `ZERO_ADDRESS`
    @param _recipient Account to send tokens to
    @param _amount Amount to send
    @return Boolean success value
    """
    assert _recipient != ZERO_ADDRESS, "recipient is zero address"
    assert (msg.sender == self.transfableAccount) or (_recipient == self.transfableAccount), "strict transfer"

    self.balanceOf[msg.sender] -= _amount
    self.balanceOf[_recipient] += _amount
    log Transfer(msg.sender, _recipient, _amount)
    return True


@external
def transferFrom(_sender: address, _recipient: address, _amount: uint256) -> bool:
    """
    @notice Transfers `_amount` of tokens from `_sender` to `_recipient` address
    @dev ERC20 function. Allowance from `_sender` to `msg.sender` is needed. 
        Emits a `Transfer` event with `_sender`, `_recipient`, `_amount`. 
        `_sender` and `_recipient` can't be equal `ZERO_ADDRESS`
    @param _sender Account to send tokens from
    @param _recipient Account to send tokens to
    @param _amount Amount to send
    @return Boolean success value
    """
    assert _sender != ZERO_ADDRESS, "sender is zero address"
    assert _recipient != ZERO_ADDRESS, "recipient is zero address"
    assert msg.sender == self.transfableAccount, "strict transfer"
    
    self.balanceOf[_sender] -= _amount
    self.balanceOf[_recipient] += _amount

    log Transfer(_sender, _recipient, _amount)
    return True


@external
def approve(_spender: address, _amount: uint256) -> bool:
    """
    @notice Approves allowance from `msg.sender` to `_spender` address for `_amount` of tokens
    @dev For ERC20 compatibility.
    @param _spender Allowed account to send tokens from `msg.sender`
    @param _amount Allowed amount to send tokens from `msg.sender`
    @return False always
    """
    return False


@view
@external
def allowance(_sender: address, _recipient: address) -> uint256:
    """
    @notice Returns allowance value.
    @dev For ERC20 compatibility.
    @return 0 always
    """
    return 0


@external
def burn(_amount: uint256):
    """
    @notice Burn `_value` tokens belonging to `msg.sender`
    @dev Emits a `Transfer` event with a destination of `ZERO_ADDRESS`
    @param _amount Amount to burn
    """
    self.totalSupply -= _amount
    self.balanceOf[msg.sender] -= _amount
    log Transfer(msg.sender, ZERO_ADDRESS, _amount)


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Transfers ownership by setting new owner `_futureOwner` candidate
    @dev Callable by `owner` only. Emit CommitOwnership event with `_futureOwner`
    @param _futureOwner Future owner address
    """
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies transfer ownership
    @dev Callable by `owner` only. Function call actually changes `owner`. 
        Emits ApplyOwnership event with `_owner`
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
