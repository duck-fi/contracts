# @version ^0.2.11
"""
@title Curve Reaper Strategy V1
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.tokens.ERC20Burnable as ERC20Burnable
import interfaces.Reaper as Reaper
import interfaces.strategies.ReaperStrategy as ReaperStrategy
import interfaces.Staker as Staker
import interfaces.Ownable as Ownable


interface UniswapV2Pair:
    def token0() -> address: nonpayable
    def getReserves() -> (uint256, uint256): nonpayable
    def swap(amount0Out: uint256, amount1Out: uint256, to: address, data: Bytes[1]): nonpayable


implements: Ownable
implements: ReaperStrategy


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


reaper: public(address)
stakerContract: public(address)
USDNCRVPairContract: public(address)
USDNDUCKSPairContract: public(address)
activated: public(bool)

admin: public(address)
owner: public(address)
futureOwner: public(address)


@external
def __init__(_reaper: address, _stakerContract: address, _USDNCRVPairContract: address, _USDNDUCKSPairContract: address):
    assert _reaper != ZERO_ADDRESS, "_reaper is not set"
    assert _stakerContract != ZERO_ADDRESS, "_stakerContract is not set"
    assert _USDNCRVPairContract != ZERO_ADDRESS, "_USDNCRVPairContract is not set"
    assert _USDNDUCKSPairContract != ZERO_ADDRESS, "_USDNDUCKSPairContract is not set"
    self.reaper = _reaper
    self.stakerContract = _stakerContract
    self.USDNCRVPairContract = _USDNCRVPairContract
    self.USDNDUCKSPairContract = _USDNDUCKSPairContract
    self.activated = False
    self.admin = msg.sender
    self.owner = msg.sender


@internal
def _getAmountOut(amountIn: uint256, reserveIn: uint256, reserveOut: uint256) -> uint256:
    assert amountIn > 0, "UniswapV2Library: INSUFFICIENT_INPUT_AMOUNT"
    assert reserveIn > 0 and reserveOut > 0, "UniswapV2Library: INSUFFICIENT_LIQUIDITY"
    amountInWithFee: uint256 = amountIn * 997
    numerator: uint256 = amountInWithFee * reserveOut
    denominator: uint256 = reserveIn * 1000 + amountInWithFee
    return numerator / denominator


@external
def invest(_amount: uint256):
    assert msg.sender == self.reaper, "reaper only"
    _stakerContract: address = self.stakerContract
    ERC20(Staker(_stakerContract).stakeToken()).transferFrom(self.reaper, _stakerContract, _amount)
    Staker(_stakerContract).stake(_amount)


@external
def reap() -> uint256:
    assert msg.sender == self.reaper, "reaper only"
    _crvToken: address = Staker(self.stakerContract).rewardToken()
    _farmToken: address = Reaper(self.reaper).farmToken()
    _claimedCrvTokens: uint256 = Staker(self.stakerContract).claim(self)
    _crvBalance: uint256 = ERC20(_crvToken).balanceOf(self)

    if _crvBalance == 0:
        return 0

    _USDNCRVPairContract: address = self.USDNCRVPairContract
    _USDNDUCKSPairContract: address = self.USDNDUCKSPairContract

    _USDNCRVPairContractToken0: address = UniswapV2Pair(_USDNCRVPairContract).token0()
    
    reserve0: uint256 = 0
    reserve1: uint256 = 0
    _usdnAmountOut: uint256 = 0
    _ducksAmountOut: uint256 = 0
    reserve0, reserve1 = UniswapV2Pair(_USDNCRVPairContract).getReserves()
    assert reserve0 > 0 and reserve1 > 0, "UniswapV2: INSUFFICIENT_LIQUIDITY"

    if _USDNCRVPairContractToken0 == _crvToken:
        _usdnAmountOut = self._getAmountOut(_crvBalance, reserve0, reserve1)
    else:
        _usdnAmountOut = self._getAmountOut(_crvBalance, reserve1, reserve0)

    _USDNDUCKSPairContractToken0: address = UniswapV2Pair(_USDNDUCKSPairContract).token0()

    reserve0, reserve1 = UniswapV2Pair(_USDNDUCKSPairContract).getReserves()
    assert reserve0 > 0 and reserve1 > 0, "UniswapV2: INSUFFICIENT_LIQUIDITY"

    if _USDNDUCKSPairContractToken0 == _farmToken:
        _ducksAmountOut = self._getAmountOut(_usdnAmountOut, reserve1, reserve0)
    else:
        _ducksAmountOut = self._getAmountOut(_usdnAmountOut, reserve0, reserve1)

    assert ERC20(_crvToken).transfer(_USDNCRVPairContract, _crvBalance)

    if _USDNCRVPairContractToken0 == _crvToken:
        UniswapV2Pair(_USDNCRVPairContract).swap(0, _usdnAmountOut, _USDNDUCKSPairContract, b"")
    else:
        UniswapV2Pair(_USDNCRVPairContract).swap(_usdnAmountOut, 0, _USDNDUCKSPairContract, b"")

    if _USDNDUCKSPairContractToken0 == _farmToken:
        UniswapV2Pair(_USDNDUCKSPairContract).swap(_ducksAmountOut, 0, self, b"")
    else:
        UniswapV2Pair(_USDNDUCKSPairContract).swap(0, _ducksAmountOut, self, b"")
    
    _farmTokenBalance: uint256 = ERC20(_farmToken).balanceOf(self)
    if _farmTokenBalance > 0:
        ERC20Burnable(_farmToken).burn(_farmTokenBalance)
    
    return _farmTokenBalance


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
def activate():
    assert msg.sender == self.owner, "owner only"
    assert not self.activated, "activated already"
    self.activated = True


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
