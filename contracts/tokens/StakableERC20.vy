# @version ^0.2.0

from vyper.interfaces import ERC20


implements: ERC20


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event Reward:
    id: uint256 
    amount: uint256

event Deprecate:
    account: indexed(address)


PERCENT_FACTOR: constant(uint256) = 10 ** 12
MULTIPLIER: constant(uint256) = 10 ** 18


_percents: uint256[MULTIPLIER]
_percents_length: uint256
_liquidTotalSupply: public(uint256)
_liquidDeposit: uint256
_balances: HashMap[address, uint256]
_deposits: HashMap[address, uint256]
_rewardIndexForAccount: HashMap[address, uint256]
_allowances: HashMap[address, HashMap[address, uint256]]
_deprecated: bool

name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)

owner: public(address)
admin: public(address)


@external
def __init__(_name: String[32], _symbol: String[4], _decimals: uint256):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals

    self._percents[self._percents_length] = PERCENT_FACTOR
    self._percents_length += 1

    self.owner = msg.sender
    self.admin = msg.sender


@external
def transferOwnership(_newOwner: address):
    assert self.owner == msg.sender or self.admin == msg.sender, "Ownable: caller is not the owner or admin"
    assert _newOwner != ZERO_ADDRESS, "Ownable: new owner is the zero address"

    self.owner = _newOwner


@external
def deprecate():
    assert self.owner == msg.sender or self.admin == msg.sender, "Ownable: caller is not the owner or admin"
    assert not self._deprecated, "Deprecateble: contract is deprecated"

    self._deprecated = True

    log Deprecate(msg.sender)


@view
@internal
def _balanceOf(account: address) -> uint256:
    account_balance: uint256 = self._balances[account]
    oldDeposit: uint256 = self._deposits[account]

    if account_balance == 0 and oldDeposit == 0:
        return 0
    
    rewardIndex: uint256 = self._rewardIndexForAccount[account]
    if rewardIndex == self._percents_length - 1:
        return account_balance + oldDeposit
    
    if oldDeposit == 0:
        profit: uint256 = self._percents[self._percents_length - 1]
        
        return profit * account_balance / self._percents[rewardIndex]
    else:
        newBalance: uint256 = account_balance * self._percents[self._percents_length - 1] / self._percents[rewardIndex]
        profit: uint256 = oldDeposit * self._percents[self._percents_length - 1] / self._percents[rewardIndex + 1]
        
        return profit + newBalance


@view
@external
def balanceOf(account: address) -> uint256: 
    return self._balanceOf(account)


@external
def deposit(account: address, amount: uint256) -> bool:
    assert self.owner == msg.sender or self.admin == msg.sender, "Ownable: caller is not the owner or admin"
    assert not self._deprecated, "Deprecateble: contract is deprecated"
    assert amount > 0, "amount should be > 0"
    assert account != ZERO_ADDRESS, "deposit to the zero address"

    liquidDeposit: uint256 = self._liquidDeposit
    self._liquidDeposit = liquidDeposit + amount

    oldDeposit: uint256 = self._deposits[account]
    if oldDeposit == 0:
        self._balances[account] = self._balanceOf(account)
        self._rewardIndexForAccount[account] = self._percents_length - 1
        self._deposits[account] = amount
    else:
        rewardIndex: uint256 = self._rewardIndexForAccount[account]
        if rewardIndex == self._percents_length - 1:
            self._deposits[account] = oldDeposit + amount
        else:
            self._balances[account] = self._balanceOf(account)
            self._rewardIndexForAccount[account] = self._percents_length - 1
            self._deposits[account] = amount

    log Transfer(ZERO_ADDRESS, account, amount)

    return True


@external
def stake(reward: uint256) -> bool:
    assert self.owner == msg.sender or self.admin == msg.sender, "Ownable: caller is not the owner or admin"
    assert not self._deprecated, "Deprecateble: contract is deprecated"
    assert reward > 0, "reward should be > 0"

    liquidTotalSupply: uint256 = self._liquidTotalSupply
    liquidDeposit: uint256 = self._liquidDeposit

    if liquidTotalSupply == 0:
        self._percents[self._percents_length] = PERCENT_FACTOR
        self._percents_length += 1
    else:
        oldPercent: uint256 = self._percents[self._percents_length - 1]
        percent: uint256 = reward * PERCENT_FACTOR / liquidTotalSupply
        newPercent: uint256 = percent + PERCENT_FACTOR
        self._percents[self._percents_length] = (newPercent * oldPercent / PERCENT_FACTOR)
        self._percents_length += 1
        liquidTotalSupply = liquidTotalSupply + reward
    
    self._liquidTotalSupply = liquidTotalSupply + liquidDeposit
    self._liquidDeposit = 0

    log Reward(self._percents_length, reward)
    return True


@external
def withdraw(account: address) -> bool:
    assert self.owner == msg.sender or self.admin == msg.sender, "Ownable: caller is not the owner or admin"
    assert not self._deprecated, "Deprecateble: contract is deprecated"

    oldDeposit: uint256 = self._deposits[account]
    rewardIndex: uint256 = self._rewardIndexForAccount[account]

    if rewardIndex == self._percents_length - 1:
        account_balance: uint256 = self._balances[account]
        self._liquidTotalSupply = self._liquidTotalSupply - account_balance
        self._liquidDeposit = self._liquidDeposit - oldDeposit

        log Transfer(account, ZERO_ADDRESS, account_balance + oldDeposit)
    else:
        account_balance: uint256 = self._balanceOf(account)
        self._liquidTotalSupply = self._liquidTotalSupply - account_balance

        log Transfer(account, ZERO_ADDRESS, account_balance)
    
    self._balances[account] = 0
    self._deposits[account] = 0

    return True


@view
@external
def totalSupply() -> uint256:
    return self._liquidTotalSupply + self._liquidDeposit


@view
@external
def allowance(owner: address, spender: address) -> uint256:
    return self._allowances[owner][spender]


@internal
def _approve(owner: address, spender: address, amount: uint256):
    assert not self._deprecated, "Deprecateble: contract is deprecated"
    assert owner != ZERO_ADDRESS, "ERC20: approve from the zero address"
    assert spender != ZERO_ADDRESS, "ERC20: approve to the zero address"

    self._allowances[owner][spender] = amount
    log Approval(owner, spender, amount)


@external
def approve(spender: address, amount: uint256) -> bool:
    self._approve(msg.sender, spender, amount)
    return True


@external
def increaseAllowance(spender: address, addedValue: uint256) -> bool:
    self._approve(msg.sender, spender, self._allowances[msg.sender][spender] + addedValue)
    return True


@external
def decreaseAllowance(spender: address, subtractedValue: uint256) -> bool:
    temp: uint256 = self._allowances[msg.sender][spender]
    assert subtractedValue <= temp, "ERC20: decreased allowance below zero"
    self._approve(msg.sender, spender, temp - subtractedValue)
    return True


@internal
def _transfer(sender: address, recipient: address, amount: uint256): 
    assert not self._deprecated, "Deprecateble: contract is deprecated"
    assert amount > 0, "amount should be > 0"
    assert sender != ZERO_ADDRESS, "ERC20: transfer from the zero address"
    assert recipient != ZERO_ADDRESS, "ERC20: transfer to the zero address"
    oldDeposit: uint256 = self._deposits[sender]
    rewardIndex: uint256 = self._rewardIndexForAccount[sender]
    depositDiff: uint256 = 0
    
    if oldDeposit == 0 or rewardIndex != self._percents_length - 1:
        senderBalance: uint256 = self._balanceOf(sender)
        assert amount <= senderBalance, "ERC20: transfer amount exceeds balance"
        self._balances[sender] = senderBalance - amount
        self._deposits[sender] = 0
        self._rewardIndexForAccount[sender] = self._percents_length - 1
    elif amount <= oldDeposit:
        self._deposits[sender] = oldDeposit - amount
        depositDiff = amount
    else:
        senderBalance: uint256 = self._balances[sender]
        assert amount - oldDeposit <= senderBalance, "ERC20: transfer amount exceeds balance"
        self._balances[sender] = senderBalance - (amount - oldDeposit)
        self._deposits[sender] = 0
        depositDiff = oldDeposit

    oldDeposit = self._deposits[recipient]
    rewardIndex = self._rewardIndexForAccount[recipient]
    if oldDeposit == 0 or rewardIndex != self._percents_length - 1:
        recipientBalance: uint256 = self._balanceOf(recipient)
        assert (amount - depositDiff) + recipientBalance >= recipientBalance, "ERC20: addition overflow for recipient balance"
        self._balances[recipient] = recipientBalance + (amount - depositDiff)
        self._rewardIndexForAccount[recipient] = self._percents_length - 1
        self._deposits[recipient] = depositDiff
    else:
        recipientBalance: uint256 = self._balances[recipient]
        self._balances[recipient] = recipientBalance + (amount - depositDiff)
        self._deposits[recipient] = oldDeposit + depositDiff

    log Transfer(sender, recipient, amount)


@external
def transfer(recipient: address, amount:uint256) -> bool:
    self._transfer(msg.sender, recipient, amount)
    return True


@external
def transferFrom(sender: address, recipient: address, amount: uint256) -> bool:
    self._transfer(sender, recipient, amount)

    temp: uint256 = self._allowances[sender][msg.sender]
    assert amount <= temp, "ERC20: transfer amount exceeds allowance"
    self._approve(sender, msg.sender, temp - amount)

    return True
