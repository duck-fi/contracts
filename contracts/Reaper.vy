# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Reaper as Reaper
import interfaces.strategies.ReaperStrategy as ReaperStrategy
import interfaces.tokens.Farmable as Farmable
import interfaces.VotingController as VotingController
import interfaces.BoostingController as BoostingController
import interfaces.GasToken as GasToken
import interfaces.AddressesCheckList as AddressesCheckList


implements: Reaper
implements: Ownable


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


VOTE_DIVIDER: constant(uint256) = 10 ** 18
ADMIN_FEE_MULTIPLYER: constant(uint256) = 10 ** 3
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
totalBoostIntegralFor: public(HashMap[address, uint256])
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
    assert _adminFee <= ADMIN_FEE_MULTIPLYER, "_adminFee > 100%"
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

    assert AddressesCheckList(self.gasTokenCheckList).get(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
def depositApprove(_spender: address, _amount: uint256):
    assert _amount == 0 or self.depositAllowance[msg.sender][_spender] == 0, "already approved"
    self.depositAllowance[msg.sender][_spender] = _amount


@internal
def _snapshot(_account: address):
    _lastSnapshotTimestampFor: uint256 = self.lastSnapshotTimestampFor[_account]
    dt: uint256 = block.timestamp - _lastSnapshotTimestampFor
    if dt == 0:
        return

    _unitCostIntegral: uint256 = self.unitCostIntegral
    _totalBalances: uint256 = self.totalBalances
    if self.isKilled == False:
        _emissionIntegral: uint256 = Farmable(self.farmToken).emissionIntegral()
        _voteIntegral: uint256 = VotingController(self.votingController).voteIntegral(self)
        _reapIntegralDiff: uint256 = (_emissionIntegral - self.emissionIntegral) * (_voteIntegral - self.voteIntegral)
        _unitCostIntegral += _reapIntegralDiff / _totalBalances
        self.emissionIntegral = _emissionIntegral
        self.voteIntegral = _voteIntegral

    _max_emission: uint256 = self.balances[_account] * (_unitCostIntegral - self.lastUnitCostIntegralFor[_account]) / VOTE_DIVIDER / dt
    _balancesIntegral: uint256 = self.balancesIntegral + _totalBalances * (block.timestamp - self.lastSnapshotTimestamp)
    # check boosting
    boost_emission: uint256 = 0
    _boostingController: address = self.boostingController
    _boostIntegral: uint256 = BoostingController(_boostingController).accountBoostIntegral(_account)
    accountBoost: uint256 = _boostIntegral - self.boostIntegralFor[_account]
    if accountBoost > 0:
        _totalBoostIntegral: uint256 = BoostingController(_boostingController).updateBoostIntegral()
        totalBoost: uint256 = _totalBoostIntegral - self.totalBoostIntegralFor[_account]
        
        if totalBoost > 0: 
            boost_emission = (_balancesIntegral - self.balancesIntegralFor[_account]) * accountBoost / totalBoost
            self.totalBoostIntegralFor[_account] = _totalBoostIntegral

        self.boostIntegralFor[_account] = _boostIntegral

    _account_emission: uint256 = min(_max_emission, _max_emission * TOKENLESS_PRODUCTION / 100 + boost_emission)
    if _account_emission != _max_emission:
        _adminFee: uint256 = self.adminFee
        if _adminFee != 0:
            self.reapIntegralFor[self] += (_max_emission - _account_emission) * _adminFee / ADMIN_FEE_MULTIPLYER

    self.reapIntegralFor[_account] += _account_emission
    self.lastSnapshotTimestampFor[_account] = block.timestamp
    self.lastSnapshotTimestamp = block.timestamp
    self.lastUnitCostIntegralFor[_account] = _unitCostIntegral
    self.balancesIntegral = _balancesIntegral
    self.balancesIntegralFor[_account] = _balancesIntegral


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
    assert _percent <= ADMIN_FEE_MULTIPLYER, "adminFee > 100%"
    self.adminFee = _percent


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
