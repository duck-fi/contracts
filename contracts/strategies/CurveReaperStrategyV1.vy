# @version ^0.2.11
"""
@title Curve Reaper Strategy V1
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.Reaper as Reaper
import interfaces.strategies.ReaperStrategy as ReaperStrategy
import interfaces.Staker as Staker
import interfaces.Ownable as Ownable


interface UniswapV2Router02:
    def swapExactTokensForTokens(amountIn: uint256, amountOutMin: uint256, path: address[3], to: address, deadline: uint256) -> uint256[3]: nonpayable


implements: Ownable
implements: ReaperStrategy


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


reaper: public(address)
stakerContract: public(address)
uniswapRouterContract: public(address)
usdnToken: public(address)
activated: public(bool)

admin: public(address)
owner: public(address)
futureOwner: public(address)


@external
def __init__(_reaper: address, _stakerContract: address, _uniswapRouterContract: address, _usdnToken: address):
    assert _reaper != ZERO_ADDRESS, "_reaper is not set"
    assert _stakerContract != ZERO_ADDRESS, "_stakerContract is not set"
    assert _uniswapRouterContract != ZERO_ADDRESS, "_uniswapRouterContract is not set"
    self.reaper = _reaper
    self.stakerContract = _stakerContract
    self.uniswapRouterContract = _uniswapRouterContract
    self.usdnToken = _usdnToken
    self.activated = False
    self.admin = msg.sender
    self.owner = msg.sender


@external
def invest(_amount: uint256):
    _stakerContract: address = self.stakerContract
    ERC20(Staker(_stakerContract).stakeToken()).transferFrom(self.reaper, _stakerContract, _amount)
    Staker(_stakerContract).stake(_amount)


@external
def reap() -> uint256:
    _crvToken: address = Staker(self.stakerContract).rewardToken()
    _farmToken: address = Reaper(self.reaper).farmToken()
    _uniswapRouterContract: address = self.uniswapRouterContract
    _claimedCrvTokens: uint256 = Staker(self.stakerContract).claim(self)
    _crvBalance: uint256 = ERC20(_crvToken).balanceOf(self)
    ERC20(_crvToken).approve(_uniswapRouterContract, _crvBalance)
    path: address[3] = [_crvToken, self.usdnToken, _farmToken]
    # UniswapV2Router02(_uniswapRouterContract).swapExactTokensForTokens(_crvBalance, 0, )
    return 0
    #TODO: swap reward


@external
def deposit(_amount: uint256):
    assert msg.sender == self.reaper, "reaper only"
    _stakerContract: address = self.stakerContract
    ERC20(Staker(_stakerContract).stakeToken()).transferFrom(self.reaper, _stakerContract, _amount)
    Staker(_stakerContract).stake(_amount)


@external
def withdraw(_amount: uint256, _account: address):
    assert msg.sender == self.reaper, "reaper only"
    assert self.activated, "not activated"
    Staker(self.stakerContract).unstake(_amount, _account)


@external
def claim(_amount: uint256, _account: address):
    assert msg.sender == self.reaper, "reaper only"
    assert self.activated, "not activated"


@view
@external
def availableToDeposit(_amount: uint256, _account: address) -> uint256:
    return _amount


@view
@external
def availableToWithdraw(_amount: uint256, _account: address) -> uint256:
    if not self.activated:
        return 0
    
    return _amount


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Transfers ownership by setting new owner `_futureOwner` candidate
    @dev Callable by owner only
    @param _futureOwner Future owner address
    """
    assert msg.sender == self.owner, "owner only"
    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies transfer ownership
    @dev Callable by owner only. Function call actually changes owner
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
