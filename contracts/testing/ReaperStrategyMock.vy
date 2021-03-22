# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.strategies.ReaperStrategy as ReaperStrategy


implements: ReaperStrategy


reaper: public(address)
lpToken: public(address)
staker: public(address)
rewardContract: public(address)

owner: public(address)
futureOwner: public(address)

isReapCalled: public(bool)
isInvestCalled: public(bool)


@external
def __init__(_lp_token: address, _reaper: address):
    assert _reaper != ZERO_ADDRESS, "_reaper is not set"
    assert _lp_token != ZERO_ADDRESS, "_lp_token is not set"
    self.reaper = _reaper
    self.lpToken = _lp_token


@external
def invest(_amount: uint256):
    assert ERC20(self.lpToken).transferFrom(self.reaper, self, _amount)
    self.isInvestCalled = True


@external
def reap():
    self.isReapCalled = True


@external
def deposit(_amount: uint256):
    assert msg.sender == self.reaper, "reaper only"
    _staker: address = self.staker
    # ERC20(Staker(_staker).stakeToken()).transferFrom(self.reaper, _staker, _amount)
    # Staker(_staker).stake(_amount)


@external
def withdraw(_amount: uint256, _account: address):
    assert msg.sender == self.reaper, "reaper only"
    # Staker(self.staker).unstake(_amount, _account)


@view
@external
def availableToDeposit(_amount: uint256, _account: address) -> uint256:
    return _amount


@view
@external
def availableToWithdraw(_amount: uint256, _account: address) -> uint256:
    return _amount
