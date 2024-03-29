# @version ^0.2.11
"""
@title Stakable ERC20 Token
@author Dispersion Finance Team
@license MIT
@notice Mintable and Stakable ERC20 token.
    `balanceOf(account) = balances[account] * p(n) / p(i)`, `p(n) = p(n-1) * (1 + reward / totalSupply)`.
    Reward is not stake for funds deposited recently.
@dev Based on the [ERC-20](https://eips.ethereum.org/EIPS/eip-20) token standard.
     [USDN](https://etherscan.io/address/0x674C6Ad92Fd080e4004b2312b45f796a192D27a0) for example.
"""

from vyper.interfaces import ERC20
import interfaces.tokens.Stakable as Stakable


implements: ERC20
implements: Stakable


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event Deprecate:
    account: indexed(address)

event Reward:
    id: uint256
    amount: uint256


PERCENT_FACTOR: constant(uint256) = 10 ** 12
MAX_RECORDS_LENGTH: constant(uint256) = 10 ** 18

owner: public(address)
admin: public(address)

name: public(String[32])
symbol: public(String[8])
decimals: public(uint256)

isDeprecated: public(bool)                                      # deprecate transfer, stake, deposit, withdraw 

percents: public(uint256[MAX_RECORDS_LENGTH])                   # percents(n) = percents(n-1) * (PERCENT_FACTOR + (PERCENT_FACTOR * reward) / _liquidTotalSupply), percents(0) = PERCENT_FACTOR
percentsLength: public(uint256)                                 # percents array length
deposits: public(HashMap[address, uint256])                     # all deposits after last stake by account
rewardIndexForAccount: public(HashMap[address, uint256])        # index of last percent by account
allowance: public(HashMap[address, HashMap[address, uint256]])  # ERC20 allowance

_balances: HashMap[address, uint256]                            # balance of account at percents[rewardIndexForAccount[account]]
_liquidDeposit: uint256                                         # all deposits after last stake
_liquidTotalSupply: uint256                                     # totalSupply - _liquidDeposit


@external
def __init__(_name: String[32], _symbol: String[8], _decimals: uint256):
    """
    @notice Contract constructor.
    @dev `owner` = `msg.sender`
    @param _name Token full name
    @param _symbol Token symbol
    @param _decimals Token decimals
    """
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.percents[0] = PERCENT_FACTOR
    self.percentsLength = 1
    self.owner = msg.sender


@view
@internal
def _balanceOf(_account: address) -> uint256:
    _accountBalance: uint256 = self._balances[_account]
    _oldDeposit: uint256 = self.deposits[_account]
    _percentsLength: uint256 = self.percentsLength

    if _accountBalance == 0 and _oldDeposit == 0:
        return 0
    
    _rewardIndex: uint256 = self.rewardIndexForAccount[_account]
    if _rewardIndex == _percentsLength - 1:
        return _accountBalance + _oldDeposit
    
    if _oldDeposit == 0:
        return self.percents[_percentsLength - 1] * _accountBalance / self.percents[_rewardIndex]
    else:
        _oldPercent: uint256 = self.percents[_percentsLength - 1]
        return (_oldDeposit * _oldPercent / self.percents[_rewardIndex + 1]) + (_accountBalance * _oldPercent / self.percents[_rewardIndex])


@view
@external
def balanceOf(_account: address = msg.sender) -> uint256:
    """
    @notice Balance of ERC20 token for `_account`.
    @dev For ERC20 compatibility.
    @param _account Address of account for balance query (`msg.sender` by default)
    @return Balance of ERC20 token
    """
    return self._balanceOf(_account)


@external
def deposit(_account: address, _amount: uint256) -> bool:
    """
    @notice Deposit tokens from other stakable network. Mint `_amount` tokens for `_account`.
    @dev Emits a `Transfer` event from `ZERO_ADDRESS` to `_account` with `_amount`. 
        `_account` can't be equal `ZERO_ADDRESS` and `_amount` must be greater `0`.
        Deposit is forbid if the contract is deprecated. Callable by `owner` only.
        Reward is not stake for funds deposited recently (after last `stake` call).
    @param _account Account to mint tokens for
    @param _amount Amount to mint
    @return Boolean success value
    """
    assert self.owner == msg.sender or self.admin == msg.sender, "owner or admin only"
    assert not self.isDeprecated, "deprecated"
    assert _amount > 0, "amount is 0"
    assert _account != ZERO_ADDRESS, "zero address"

    liquidDeposit: uint256 = self._liquidDeposit
    self._liquidDeposit = liquidDeposit + _amount

    _oldDeposit: uint256 = self.deposits[_account]
    if _oldDeposit == 0:
        self._balances[_account] = self._balanceOf(_account)
        self.rewardIndexForAccount[_account] = self.percentsLength - 1
        self.deposits[_account] = _amount
    else:
        _rewardIndex: uint256 = self.rewardIndexForAccount[_account]
        if _rewardIndex == self.percentsLength - 1:
            self.deposits[_account] = _oldDeposit + _amount
        else:
            self._balances[_account] = self._balanceOf(_account)
            self.rewardIndexForAccount[_account] = self.percentsLength - 1
            self.deposits[_account] = _amount

    log Transfer(ZERO_ADDRESS, _account, _amount)
    return True


@external
def stake(_reward: uint256) -> bool:
    """
    @notice Stake reward. Mint `_reward` tokens for all holders immediently (low cost).
    @dev Emits a `Reward` event. `_reward` must be greater `0`.
        Deposit is forbid if the contract is deprecated. Callable by `owner` only.
        Reward is not stake for funds deposited recently (after last `stake` call) and first call.
    @param _reward Amount to mint reward
    @return Boolean success value
    """
    assert self.owner == msg.sender or self.admin == msg.sender, "owner or admin only"
    assert not self.isDeprecated, "deprecated"
    assert _reward > 0, "reward is 0"

    liquidTotalSupply: uint256 = self._liquidTotalSupply
    liquidDeposit: uint256 = self._liquidDeposit
    _percentsLength: uint256 = self.percentsLength

    if liquidTotalSupply == 0:
        self.percents[_percentsLength] = self.percents[_percentsLength - 1]
    else:
        _oldPercent: uint256 = self.percents[_percentsLength - 1]
        _newPercent: uint256 = _reward * PERCENT_FACTOR / liquidTotalSupply + PERCENT_FACTOR
        self.percents[_percentsLength] = (_newPercent * _oldPercent / PERCENT_FACTOR)
        liquidTotalSupply = liquidTotalSupply + _reward
    
    self.percentsLength = _percentsLength + 1
    self._liquidTotalSupply = liquidTotalSupply + liquidDeposit
    self._liquidDeposit = 0

    log Reward(_percentsLength + 1, _reward)
    return True


@external
def withdraw(_account: address) -> bool:
    """
    @notice Withdraw tokens back to other stakable network. Burn all token balance for `_account`.
    @dev Emits a `Transfer` event from `_account` to `ZERO_ADDRESS` for all token balance. 
        Deposit is forbid if the contract is deprecated. Callable by `owner` only.
    @param _account Account for burn all tokens
    @return Boolean success value
    """
    assert self.owner == msg.sender or self.admin == msg.sender, "owner or admin only"
    assert not self.isDeprecated, "deprecated"

    _oldDeposit: uint256 = self.deposits[_account]
    _rewardIndex: uint256 = self.rewardIndexForAccount[_account]

    if _rewardIndex == self.percentsLength - 1:
        _accountBalance: uint256 = self._balances[_account]
        self._liquidTotalSupply -= _accountBalance
        self._liquidDeposit -= _oldDeposit
        log Transfer(_account, ZERO_ADDRESS, _accountBalance + _oldDeposit)
    else:
        _accountBalance: uint256 = self._balanceOf(_account)
        self._liquidTotalSupply -=  _accountBalance
        log Transfer(_account, ZERO_ADDRESS, _accountBalance)
    
    self._balances[_account] = 0
    self.deposits[_account] = 0
    return True


@internal
def _approve(_owner: address, _spender: address, _amount: uint256):
    assert not self.isDeprecated, "deprecated"
    assert _owner != ZERO_ADDRESS, "owner is zero address"
    assert _spender != ZERO_ADDRESS, "spender is zero address"

    self.allowance[_owner][_spender] = _amount
    log Approval(_owner, _spender, _amount)


@external
def approve(_spender: address, _amount: uint256) -> bool:
    """
    @notice Approves allowance from `msg.sender` to `_spender` address for `_amount` of tokens
    @dev ERC20 function. Emits a `Approval` event with `msg.sender`, `_spender`, `_amount`.
    @param _spender Allowed account to send tokens from `msg.sender`
    @param _amount Allowed amount to send tokens from `msg.sender`
    @return Boolean success value
    """
    self._approve(msg.sender, _spender, _amount)
    return True


@internal
def _transfer(_sender: address, _recipient: address, _amount: uint256): 
    assert not self.isDeprecated, "deprecated"
    assert _recipient != ZERO_ADDRESS, "recipient is zero address"
    _oldDeposit: uint256 = self.deposits[_sender]
    _rewardIndex: uint256 = self.rewardIndexForAccount[_sender]
    _percentsLength: uint256 = self.percentsLength
    _depositDiff: uint256 = 0
    
    if _oldDeposit == 0 or _rewardIndex != _percentsLength - 1:
        self._balances[_sender] = self._balanceOf(_sender) - _amount
        self.rewardIndexForAccount[_sender] = _percentsLength - 1
        self.deposits[_sender] = 0
    elif _amount <= _oldDeposit:
        self.deposits[_sender] = _oldDeposit - _amount
        _depositDiff = _amount
    else:
        self._balances[_sender] = self._balances[_sender] - (_amount - _oldDeposit)
        self.deposits[_sender] = 0
        _depositDiff = _oldDeposit

    _oldDeposit = self.deposits[_recipient]
    _rewardIndex = self.rewardIndexForAccount[_recipient]
    if _oldDeposit == 0 or _rewardIndex != _percentsLength - 1:
        self._balances[_recipient] = self._balanceOf(_recipient) + (_amount - _depositDiff)
        self.rewardIndexForAccount[_recipient] = _percentsLength - 1
        self.deposits[_recipient] = _depositDiff
    else:
        self._balances[_recipient] = self._balances[_recipient] + (_amount - _depositDiff)
        self.deposits[_recipient] = _oldDeposit + _depositDiff

    log Transfer(_sender, _recipient, _amount)


@external
def transfer(_recipient: address, _amount:uint256) -> bool:
    """
    @notice Transfers `_amount` of tokens from `msg.sender` to `_recipient` address
    @dev ERC20 function. Emits a `Transfer` event with `msg.sender`, `_recipient`, `_amount`. 
        `_recipient` can't be equal `ZERO_ADDRESS`
    @param _recipient Account to send tokens to
    @param _amount Amount to send
    @return Boolean success value
    """
    self._transfer(msg.sender, _recipient, _amount)
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
    self._transfer(_sender, _recipient, _amount)
    self._approve(_sender, msg.sender, self.allowance[_sender][msg.sender] - _amount)
    return True


@view
@external
def totalSupply() -> uint256:
    """
    @notice Total supply of tokens.
    @dev ERC20 function.
    @return Uint256 Total supply
    """
    return self._liquidTotalSupply + self._liquidDeposit


@external
def transferOwnership(_newOwner: address):
    """
    @notice Transfers ownership by setting new owner `_newOwner`.
    @dev Callable by owner only. `_newOwner` can't be equal `ZERO_ADDRESS`.
    @param _newOwner New `owner` address
    """
    assert self.owner == msg.sender, "owner only"
    assert _newOwner != ZERO_ADDRESS, "zero address"
    self.owner = _newOwner



@external
def setAdmin(_newAdmin: address):
    """
    @notice Transfers ownership by setting new admin `_newAdmin`.
    @dev Callable by owner only. `_newOwner` can't be equal `ZERO_ADDRESS`.
    @param _newAdmin New `admin` address
    """
    assert self.owner == msg.sender or self.admin == msg.sender, "owner or admin only"
    assert _newAdmin != ZERO_ADDRESS, "zero address"
    self.admin = _newAdmin



@external
def deprecate():
    """
    @notice Deprecate contract.
    @dev Callable by owner only.
    """
    assert self.owner == msg.sender or self.admin == msg.sender, "only owner or admin"
    self.isDeprecated = True
    log Deprecate(msg.sender)
