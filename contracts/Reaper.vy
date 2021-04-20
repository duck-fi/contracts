# @version ^0.2.11
"""
@title Reaper
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Reaper as Reaper
import interfaces.strategies.ReaperStrategy as ReaperStrategy
import interfaces.tokens.Farmable as Farmable
import interfaces.Controller as Controller
import interfaces.VotingController as VotingController
import interfaces.BoostingController as BoostingController
import interfaces.GasToken as GasToken
import interfaces.WhiteList as WhiteList


implements: Reaper
implements: Ownable


event Deposit:
    account: address
    amount: uint256
    feeOptimization: bool

event Withdraw:
    account: address
    amount: uint256

event Kill:
    admin: address

event Unkill:
    admin: address

event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


VOTE_DIVIDER: constant(uint256) = 10 ** 18
ADMIN_FEE_MULTIPLIER: constant(uint256) = 10 ** 3
MIN_GAS_CONSTANT: constant(uint256) = 21_000
BOOST_AMPLIFIER_PERCENT: constant(uint256) = 50


lpToken: public(address)
farmToken: public(address)

controller: public(address)
votingController: public(address)
boostingController: public(address)

reaperStrategy: public(address)
gasTokenCheckList: public(address)

balances: public(HashMap[address, uint256])
totalBalances: public(uint256)
depositAllowance: public(HashMap[address, HashMap[address, uint256]])
balancesIntegral: public(uint256)
balancesIntegralFor: public(HashMap[address, uint256])
reapIntegral: public(uint256)
reapIntegralFor: public(HashMap[address, uint256])
unitCostIntegral: public(uint256)
lastUnitCostIntegralFor: public(HashMap[address, uint256])
lastSnapshotTimestamp: public(uint256)
lastSnapshotTimestampFor: public(HashMap[address, uint256])
emissionIntegral: public(uint256)
voteIntegral: public(uint256)
boostIntegralFor: public(HashMap[address, uint256])
adminFee: public(uint256)
isKilled: public(bool)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_lpToken: address, _farmToken: address, _controller: address, _gasTokenCheckList: address, _adminFee: uint256):
    assert _lpToken != ZERO_ADDRESS, "_lpToken is not set"
    assert _controller != ZERO_ADDRESS, "_controller is not set"
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"
    assert _farmToken != ZERO_ADDRESS, "_farmToken is not set"
    assert _adminFee <= ADMIN_FEE_MULTIPLIER, "_adminFee > 100%"
    self.lpToken = _lpToken
    self.controller = _controller
    self.votingController = Controller(_controller).votingController()
    self.boostingController = Controller(_controller).boostingController()
    self.gasTokenCheckList = _gasTokenCheckList
    self.farmToken = _farmToken
    self.adminFee = _adminFee
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert WhiteList(self.gasTokenCheckList).check(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
@nonreentrant('lock')
def depositApprove(_spender: address, _amount: uint256):
    assert _amount == 0 or self.depositAllowance[msg.sender][_spender] == 0, "already approved"
    self.depositAllowance[msg.sender][_spender] = _amount


@internal
def _snapshot(_account: address):
    _lastSnapshotTimestampFor: uint256 = self.lastSnapshotTimestampFor[_account]
    self.lastSnapshotTimestampFor[_account] = block.timestamp

    _lastSnapshotTimestamp: uint256 = self.lastSnapshotTimestamp
    if _lastSnapshotTimestamp == 0:
        self.lastSnapshotTimestamp = block.timestamp
        self.emissionIntegral = Farmable(self.farmToken).emissionIntegral()
        self.voteIntegral = VotingController(self.votingController).voteIntegral(self)
        self.lastSnapshotTimestampFor[_account] = block.timestamp
        self.boostIntegralFor[_account] = BoostingController(self.boostingController).updateAccountBoostFactorIntegral(_account)
        return
    
    _unitCostIntegral: uint256 = self.unitCostIntegral
    _oldBalancesIntegral: uint256 = self.balancesIntegral
    _balancesIntegral: uint256 = _oldBalancesIntegral
    _totalBalances: uint256 = self.totalBalances
    if block.timestamp > _lastSnapshotTimestamp:
        # update reaper integrals
        _emissionIntegral: uint256 = Farmable(self.farmToken).emissionIntegral()
        _voteIntegral: uint256 = VotingController(self.votingController).voteIntegral(self)

        if _emissionIntegral > 0 and self.emissionIntegral == 0:
            _oldBalancesIntegral = 0
            _balancesIntegral = _totalBalances * (block.timestamp - Farmable(self.farmToken).startEmissionTimestamp())
        elif _emissionIntegral > 0:
            _balancesIntegral = _totalBalances * (block.timestamp - _lastSnapshotTimestamp) + _oldBalancesIntegral
        
        if _balancesIntegral > _oldBalancesIntegral and not self.isKilled:
            _unitCostIntegral += (_emissionIntegral - self.emissionIntegral) * (_voteIntegral - self.voteIntegral) / (_balancesIntegral - _oldBalancesIntegral)
            self.unitCostIntegral = _unitCostIntegral
        
        self.balancesIntegral = _balancesIntegral
        self.emissionIntegral = _emissionIntegral
        self.voteIntegral = _voteIntegral
        self.lastSnapshotTimestamp = block.timestamp
    
    if _lastSnapshotTimestampFor == 0:
        self.lastUnitCostIntegralFor[_account] = _unitCostIntegral
        self.lastSnapshotTimestampFor[_account] = block.timestamp
        self.boostIntegralFor[_account] = BoostingController(self.boostingController).updateAccountBoostFactorIntegral(_account)
        self.balancesIntegralFor[_account] = _balancesIntegral
        return

    dt: uint256 = block.timestamp - _lastSnapshotTimestampFor
    if dt == 0:
        return

    _boostingController: address = self.boostingController
    _boostIntegral: uint256 = BoostingController(_boostingController).updateAccountBoostFactorIntegral(_account)
    _accountBalanceIntegral: uint256 = (self.balances[_account] * dt * VOTE_DIVIDER * BOOST_AMPLIFIER_PERCENT / 100 + (_balancesIntegral - self.balancesIntegralFor[_account]) * (_boostIntegral - self.boostIntegralFor[_account]) * (100 - BOOST_AMPLIFIER_PERCENT) / 100 / dt) / VOTE_DIVIDER

    _maxEmission: uint256 = self.balances[_account] * (_unitCostIntegral - self.lastUnitCostIntegralFor[_account]) / VOTE_DIVIDER
    _accountEmission: uint256 = min(_maxEmission, _accountBalanceIntegral * (_unitCostIntegral - self.lastUnitCostIntegralFor[_account]) / dt / VOTE_DIVIDER)
    if _accountEmission != _maxEmission:
        _adminFee: uint256 = self.adminFee
        if _adminFee != 0:
            self.reapIntegralFor[self] += (_maxEmission - _accountEmission) * _adminFee / ADMIN_FEE_MULTIPLIER

    self.reapIntegral += _accountEmission
    self.reapIntegralFor[_account] += _accountEmission
    self.lastUnitCostIntegralFor[_account] = _unitCostIntegral
    self.balancesIntegralFor[_account] = _balancesIntegral
    self.boostIntegralFor[_account] = _boostIntegral


@external
@nonreentrant('lock')
def deposit(_amount: uint256, _account: address = msg.sender, _feeOptimization: bool = False, _gasToken: address = ZERO_ADDRESS):
    assert not self.isKilled, "reaper is killed"
    
    _gasStart: uint256 = msg.gas
    
    if _account != msg.sender:
        _allowance: uint256 = self.depositAllowance[_account][msg.sender]
        if _allowance != MAX_UINT256:
            self.depositAllowance[_account][msg.sender] = _allowance - _amount

    self._snapshot(_account)
    assert ERC20(self.lpToken).transferFrom(msg.sender, self, _amount)
    self.totalBalances += _amount

    _reaperStrategy: address = self.reaperStrategy
    if _reaperStrategy != ZERO_ADDRESS:
        _availableAmount: uint256 = ReaperStrategy(_reaperStrategy).availableToDeposit(_amount, _account)
        self.balances[_account] += _availableAmount

        if _amount - _availableAmount > 0:
            self.balances[self] += _amount - _availableAmount

        if _feeOptimization == False:
            ReaperStrategy(_reaperStrategy).deposit(_amount)
    else:
        self.balances[_account] += _amount

    log Deposit(_account, _amount, _feeOptimization)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 4)


@external
@nonreentrant('lock')
def invest(_gasToken: address = ZERO_ADDRESS):
    _gasStart: uint256 = msg.gas
    _amount: uint256 = ERC20(self.lpToken).balanceOf(self)
    if _amount == 0:
        return

    _reaperStrategy: address = self.reaperStrategy
    if _reaperStrategy != ZERO_ADDRESS:
        ReaperStrategy(_reaperStrategy).invest(_amount)
    
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 1)


@external
@nonreentrant('lock')
def reap(_gasToken: address = ZERO_ADDRESS) -> uint256:
    _gasStart: uint256 = msg.gas
    _reapedAmount: uint256 = 0
    
    _reaperStrategy: address = self.reaperStrategy
    if _reaperStrategy != ZERO_ADDRESS:
        _reapedAmount = ReaperStrategy(_reaperStrategy).reap()
    
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 1)

    return _reapedAmount


@external
@nonreentrant('lock')
def withdraw(_amount: uint256, _gasToken: address = ZERO_ADDRESS):    
    _gasStart: uint256 = msg.gas

    self._snapshot(msg.sender)

    _availableAmount: uint256 = _amount
    _reaperStrategy: address = self.reaperStrategy
    _lpToken: address = self.lpToken

    if _reaperStrategy != ZERO_ADDRESS:
        _availableAmount = ReaperStrategy(_reaperStrategy).availableToWithdraw(_amount, msg.sender)
        assert _availableAmount > 0, "withdraw is locked"
        _lpBalance: uint256 = ERC20(_lpToken).balanceOf(self)
        
        if _lpBalance >= _availableAmount:
            assert ERC20(_lpToken).transfer(msg.sender, _availableAmount)
        elif _lpBalance > 0:
            assert ERC20(_lpToken).transfer(msg.sender, _lpBalance)
            ReaperStrategy(_reaperStrategy).withdraw(_availableAmount - _lpBalance, msg.sender)
        else:
            ReaperStrategy(_reaperStrategy).withdraw(_availableAmount, msg.sender)

        if _amount - _availableAmount > 0:
            self.balances[self] += _amount - _availableAmount
    else:
        assert ERC20(_lpToken).transfer(msg.sender, _amount)
    
    self.balances[msg.sender] -= _amount
    self.totalBalances -= _availableAmount

    log Withdraw(msg.sender, _amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@external
@nonreentrant('lock')
def snapshot(_account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):    
    _gasStart: uint256 = msg.gas
    self._snapshot(_account)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@external
def setReaperStrategy(_reaperStrategy: address):
    assert msg.sender == self.owner, "owner only"

    _lpToken: address = self.lpToken
    oldReaperStrategy: address = self.reaperStrategy
    if oldReaperStrategy != ZERO_ADDRESS:
        assert ERC20(_lpToken).approve(oldReaperStrategy, 0)

    assert ERC20(_lpToken).approve(_reaperStrategy, MAX_UINT256)
    self.depositAllowance[self][_reaperStrategy] = MAX_UINT256
    self.reaperStrategy = _reaperStrategy


@external
def kill():
    assert msg.sender == self.owner, "owner only"
    self.isKilled = True
    log Kill(msg.sender)


@external
def unkill():
    assert msg.sender == self.owner, "owner only"
    self.isKilled = False
    log Unkill(msg.sender)


@external
def setAdminFee(_percent: uint256):
    assert msg.sender == self.owner, "owner only"
    assert _percent <= ADMIN_FEE_MULTIPLIER, "adminFee > 100%"
    self.adminFee = _percent


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
    @dev Callable by `owner` only. Function call actually changes `owner`. 
        Emits ApplyOwnership event with `_owner`
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
