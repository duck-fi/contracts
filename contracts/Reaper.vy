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
import interfaces.VotingController as VotingController
import interfaces.BoostingController as BoostingController
import interfaces.GasToken as GasToken
import interfaces.WhiteList as WhiteList


implements: Reaper
implements: Ownable


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


VOTE_DIVIDER: constant(uint256) = 10 ** 18
ADMIN_FEE_MULTIPLIER: constant(uint256) = 10 ** 3
MIN_GAS_CONSTANT: constant(uint256) = 21_000
TOKENLESS_PRODUCTION: constant(uint256) = 50


lpToken: public(address)
farmToken: public(address)
controller: public(address)
reaperStrategy: public(address)
gasTokenCheckList: public(address)
votingController: public(address)
boostingController: public(address)

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
# totalBoostIntegralFor: public(HashMap[address, uint256])
adminFee: public(uint256)
isKilled: public(bool)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_lpToken: address, _farmToken: address, _controller: address, _votingController: address, _boostingController: address, _gasTokenCheckList: address, _adminFee: uint256):
    assert _lpToken != ZERO_ADDRESS, "_lpToken is not set"
    assert _controller != ZERO_ADDRESS, "_controller is not set"
    assert _votingController != ZERO_ADDRESS, "_votingController is not set"
    assert _boostingController != ZERO_ADDRESS, "_boostingController is not set"
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"
    assert _farmToken != ZERO_ADDRESS, "_farmToken is not set"
    assert _adminFee <= ADMIN_FEE_MULTIPLIER, "_adminFee > 100%"
    self.lpToken = _lpToken
    self.controller = _controller
    self.votingController = _votingController
    self.boostingController = _boostingController
    self.gasTokenCheckList = _gasTokenCheckList
    self.farmToken = _farmToken
    self.adminFee = _adminFee
    self.owner = msg.sender
    assert ERC20(_farmToken).approve(_controller, MAX_UINT256)


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert WhiteList(self.gasTokenCheckList).check(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
def depositApprove(_spender: address, _amount: uint256):
    assert _amount == 0 or self.depositAllowance[msg.sender][_spender] == 0, "already approved"
    self.depositAllowance[msg.sender][_spender] = _amount


debugg:public(uint256)
debug1:public(uint256)
debug2:public(uint256)
debug3:public(uint256)
debuggg:public(uint256)
@internal
def _snapshot(_account: address):
    # emission is not started:
        # true - return
        # false - cont

    # reaper is not initialized:
        # true - init reaper integrals and user integrals
        # false - cont
    
    # reaper is killed:
        # true - do not update reaper integrals
        # false - update reaper integrals and cont
    # update user integrals

    _lastSnapshotTimestampFor: uint256 = self.lastSnapshotTimestampFor[_account]
    self.lastSnapshotTimestampFor[_account] = block.timestamp
    
    # if _emissionIntegral == 0:
        # return

    _lastSnapshotTimestamp: uint256 = self.lastSnapshotTimestamp
    if _lastSnapshotTimestamp == 0:
        # init reaper integrals
        self.lastSnapshotTimestamp = block.timestamp
        self.emissionIntegral = Farmable(self.farmToken).emissionIntegral()
        self.voteIntegral = VotingController(self.votingController).voteIntegral(self)
        # init user integrals TODO: need this?
        _boostingController: address = self.boostingController
        self.lastSnapshotTimestampFor[_account] = block.timestamp
        # self.totalBoostIntegralFor[_account] = BoostingController(_boostingController).updateBoostIntegral()
        self.boostIntegralFor[_account] = BoostingController(_boostingController).updateAccountBoostFactorIntegral(_account)
        return
    
    _unitCostIntegral: uint256 = self.unitCostIntegral
    _oldBalancesIntegral: uint256 = self.balancesIntegral
    _balancesIntegral: uint256 = _oldBalancesIntegral
    _totalBalances: uint256 = self.totalBalances
    if not self.isKilled and block.timestamp > _lastSnapshotTimestamp:
        # update reaper integrals
        _emissionIntegral: uint256 = Farmable(self.farmToken).emissionIntegral()
        _voteIntegral: uint256 = VotingController(self.votingController).voteIntegral(self)

        if _emissionIntegral > 0 and self.emissionIntegral == 0:
            _oldBalancesIntegral = 0
            _balancesIntegral = _totalBalances * (block.timestamp - Farmable(self.farmToken).startEmissionTimestamp())
        elif _emissionIntegral > 0: # TODO: HERE _balancesIntegral CAN REDUCE!!!! in that case (_balancesIntegral - oldbalancesIntegal) < 0 !!!
            _balancesIntegral = _totalBalances * (block.timestamp - _lastSnapshotTimestamp) + _oldBalancesIntegral
        
        if _balancesIntegral > _oldBalancesIntegral:
            _unitCostIntegral += (_emissionIntegral - self.emissionIntegral) * (_voteIntegral - self.voteIntegral) / (_balancesIntegral - _oldBalancesIntegral)
            self.unitCostIntegral = _unitCostIntegral
        self.balancesIntegral = _balancesIntegral
        self.emissionIntegral = _emissionIntegral
        self.voteIntegral = _voteIntegral
        self.lastSnapshotTimestamp = block.timestamp
    
    if _lastSnapshotTimestampFor == 0:
        # init user integrals
        _boostingController: address = self.boostingController
        self.lastUnitCostIntegralFor[_account] = _unitCostIntegral
        self.lastSnapshotTimestampFor[_account] = block.timestamp
        # self.totalBoostIntegralFor[_account] = BoostingController(_boostingController).updateBoostIntegral()
        self.boostIntegralFor[_account] = BoostingController(_boostingController).updateAccountBoostFactorIntegral(_account)
        self.balancesIntegralFor[_account] = _balancesIntegral
        return

    # dt: uint256 = block.timestamp - _lastSnapshotTimestampFor
    # if dt == 0:
    #     return

    # _totalBalances: uint256 = self.totalBalances
    # if _totalBalances == 0:
    #     self.debugg = 3
    #     if self.lastSnapshotTimestamp == 0:
    #         self.debugg = 4
    #         _boostingController: address = self.boostingController
    #         self.lastSnapshotTimestamp = block.timestamp
    #         self.emissionIntegral = Farmable(self.farmToken).emissionIntegral()
    #         self.voteIntegral = VotingController(self.votingController).voteIntegral(self)
    #         self.lastSnapshotTimestampFor[_account] = block.timestamp
    #         self.totalBoostIntegralFor[_account] = BoostingController(_boostingController).updateBoostIntegral()
    #         self.boostIntegralFor[_account] = BoostingController(_boostingController).accountBoostIntegral(_account)
    #         return # HERE IS AN ERROR

    # _unitCostIntegral: uint256 = self.unitCostIntegral
    # _oldBalancesIntegral: uint256 = self.balancesIntegral
    # self.debugg = 5
    # _balancesIntegral: uint256 = _oldBalancesIntegral + _totalBalances * (block.timestamp - self.lastSnapshotTimestamp)
    # self.debugg = 6
    # if self.isKilled == False:
    #     self.debugg = 7
    #     _emissionIntegral: uint256 = Farmable(self.farmToken).emissionIntegral()
    #     _voteIntegral: uint256 = VotingController(self.votingController).voteIntegral(self)
    #     self.debugg = 8
    #     if (block.timestamp - self.lastSnapshotTimestamp) > 0:
    #         if _balancesIntegral > _oldBalancesIntegral and _emissionIntegral > 0 and _voteIntegral > 0:
    #             if self.emissionIntegral == 0 and _emissionIntegral > 0:
    #                 _oldBalancesIntegral = 0
    #                 _balancesIntegral = _totalBalances * (block.timestamp - Farmable(self.farmToken).startEmissionTimestamp())
    #             self.debugg = 9
    #             self.debuggg = (_emissionIntegral - self.emissionIntegral) * (_voteIntegral - self.voteIntegral) / (_balancesIntegral - _oldBalancesIntegral)
    #             _unitCostIntegral += (_emissionIntegral - self.emissionIntegral) * (_voteIntegral - self.voteIntegral) / (_balancesIntegral - _oldBalancesIntegral)
    #             self.unitCostIntegral = _unitCostIntegral
    #             self.balancesIntegral = _balancesIntegral
    #             self.emissionIntegral = _emissionIntegral
    #             self.voteIntegral = _voteIntegral
    #             self.lastSnapshotTimestamp = block.timestamp

    # self.debugg = 10
    # _lastSnapshotTimestampFor: uint256 = self.lastSnapshotTimestampFor[_account]
    # if _lastSnapshotTimestampFor == 0:
    #     self.debugg = 11
    #     _boostingController: address = self.boostingController
    #     self.lastSnapshotTimestampFor[_account] = block.timestamp
    #     self.totalBoostIntegralFor[_account] = BoostingController(_boostingController).updateBoostIntegral()
    #     self.boostIntegralFor[_account] = BoostingController(_boostingController).accountBoostIntegral(_account)
    #     self.lastUnitCostIntegralFor[_account] = _unitCostIntegral
    #     return

    dt: uint256 = block.timestamp - _lastSnapshotTimestampFor
    if dt == 0:
        return

    # check boosting
    # boost_balance: uint256 = 0
    _boostingController: address = self.boostingController
    _boostIntegral: uint256 = BoostingController(_boostingController).updateAccountBoostFactorIntegral(_account)
    # TODO: optimize accuracy 
    accountBoost: uint256 = (_balancesIntegral - self.balancesIntegralFor[_account]) * (_boostIntegral - self.boostIntegralFor[_account]) #/ dt / VOTE_DIVIDER
    # self.debug1 = accountBoost
    # self.debug2 = (_balancesIntegral - self.balancesIntegralFor[_account])
    # self.debug3 = (_boostIntegral - self.boostIntegralFor[_account])

    # if accountBoost > 0:
    #     # _totalBoostIntegral: uint256 = BoostingController(_boostingController).updateBoostIntegral()
    #     # totalBoost: uint256 = _totalBoostIntegral - self.totalBoostIntegralFor[_account]
        
    #     if totalBoost > 0: 
    #         boost_balance = (_balancesIntegral - self.balancesIntegralFor[_account]) / dt * accountBoost / totalBoost
    #         self.totalBoostIntegralFor[_account] = _totalBoostIntegral


    self.debug1 = accountBoost
    self.debug2 = accountBoost * (100 - TOKENLESS_PRODUCTION) / 100
    self.debug3 = (self.balances[_account] * dt * VOTE_DIVIDER * TOKENLESS_PRODUCTION / 100 + (_balancesIntegral - self.balancesIntegralFor[_account]) * (_boostIntegral - self.boostIntegralFor[_account]) * (100 - TOKENLESS_PRODUCTION) / 100 / dt) / VOTE_DIVIDER

    _max_emission: uint256 = self.balances[_account] * (_unitCostIntegral - self.lastUnitCostIntegralFor[_account]) / VOTE_DIVIDER
    _account_emission: uint256 = self.debug3 * (_unitCostIntegral - self.lastUnitCostIntegralFor[_account]) / dt / VOTE_DIVIDER
    _account_emission = min(_max_emission, _account_emission)
    if _account_emission != _max_emission:
        _adminFee: uint256 = self.adminFee
        if _adminFee != 0:
            self.reapIntegralFor[self] += (_max_emission - _account_emission) * _adminFee / ADMIN_FEE_MULTIPLIER

    self.reapIntegral += _account_emission
    self.reapIntegralFor[_account] += _account_emission
    self.lastUnitCostIntegralFor[_account] = _unitCostIntegral
    self.balancesIntegralFor[_account] = _balancesIntegral
    self.boostIntegralFor[_account] = _boostIntegral


@external
@nonreentrant('lock')
def deposit(_amount: uint256, _account: address = msg.sender, _feeOptimization: bool = False, _gasToken: address = ZERO_ADDRESS):
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
def reap(_gasToken: address = ZERO_ADDRESS):
    _gasStart: uint256 = msg.gas
    _reaperStrategy: address = self.reaperStrategy
    if _reaperStrategy != ZERO_ADDRESS:
        ReaperStrategy(_reaperStrategy).reap()
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 1)


@external
@nonreentrant('lock')
def withdraw(_amount: uint256, _gasToken: address = ZERO_ADDRESS):    
    _gasStart: uint256 = msg.gas

    self._snapshot(msg.sender)

    _availableAmount: uint256 = _amount
    _reaperStrategy: address = self.reaperStrategy
    if _reaperStrategy != ZERO_ADDRESS:
        _availableAmount = ReaperStrategy(_reaperStrategy).availableToWithdraw(_amount, msg.sender)

        if _availableAmount > 0:
            _lpToken: address = self.lpToken
            _lpBalance: uint256 = ERC20(_lpToken).balanceOf(self)

            if _lpBalance >= _availableAmount:
                ERC20(self.lpToken).transfer(msg.sender, _availableAmount)
            elif _lpBalance > 0:
                ERC20(self.lpToken).transfer(msg.sender, _lpBalance)
                ReaperStrategy(_reaperStrategy).withdraw(_availableAmount - _lpBalance, msg.sender)
            else:
                ReaperStrategy(_reaperStrategy).withdraw(_availableAmount, msg.sender)

            if _amount - _availableAmount > 0:
                self.balances[self] += _amount - _availableAmount
    else:
        ERC20(self.lpToken).transfer(msg.sender, _amount)
    
    self.balances[msg.sender] -= _availableAmount
    self.totalBalances -= _availableAmount

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@external
def snapshot(_account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):    
    _gasStart: uint256 = msg.gas
    self._snapshot(_account)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 2)


@external
def setReaperStrategy(_reaperStrategy: address):
    assert msg.sender == self.owner, "owner only"
    assert ERC20(self.lpToken).approve(_reaperStrategy, MAX_UINT256)
    self.depositAllowance[self][_reaperStrategy] = MAX_UINT256
    self.reaperStrategy = _reaperStrategy


@external
def kill():
    assert msg.sender == self.owner, "owner only"
    self.isKilled = True


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
