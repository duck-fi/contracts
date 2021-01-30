# @version ^0.2.0


from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Reaper as Reaper
import interfaces.strategies.ReaperStrategy as ReaperStrategy
import interfaces.tokens.Farmable as Farmable
import interfaces.VotingController as VotingController


implements: Reaper
implements: Ownable


event CommitOwnership:
    owner: address

event ApplyOwnership:
    owner: address


VOTE_DIVIDER: constant(uint256) = 10 ** 18


lpToken: public(address)
farmToken: public(address)
controller: public(address)
reaperStrategy: public(address)
votingController: public(address)
balances: public(HashMap[address, uint256])
depositAllowance: public(HashMap[address, HashMap[address, uint256]])
totalBalances: public(uint256)
isKilled: public(bool)
reapIntegral: public(uint256)
reapIntegralFor: public(HashMap[address, uint256])
unitCostIntegral: public(uint256)
lastReapTimestampFor: public(HashMap[address, uint256])
lastUnitCostIntegralFor: public(HashMap[address, uint256])
emissionIntegral: public(uint256)
voteIntegral: public(uint256)

owner: public(address)
futureOwner: public(address)


@external
def __init__(_lpToken: address, _farmToken: address, _controller: address, _votingController: address):
    self.lpToken = _lpToken
    self.controller = _controller
    self.votingController = _votingController
    self.farmToken = _farmToken

    ERC20(_farmToken).approve(_controller, MAX_UINT256)


@external
def depositApprove(_spender: address, _amount:uint256):
    assert _amount == 0 or self.depositAllowance[msg.sender][_spender] == 0, "already approved"
    self.depositAllowance[msg.sender][_spender] = _amount


@internal
def _snapshot(_account: address):
    _emissionIntegral: uint256 = Farmable(self.farmToken).emissionIntegral()
    _voteIntegral: uint256 = VotingController(self.votingController).reaperIntegratedVotes(self)


    _reapIntegralDiff: uint256 = 0
    _unitCostIntegralDiff: uint256 = 0
    _unitCostIntegral: uint256 = self.unitCostIntegral
    if self.isKilled == False:
        _reapIntegralDiff = (_emissionIntegral - self.emissionIntegral) * (_voteIntegral - self.voteIntegral)
        _unitCostIntegral += _reapIntegralDiff / self.totalBalances
        self.emissionIntegral = _emissionIntegral
        self.voteIntegral = _voteIntegral
        self.reapIntegral += _reapIntegralDiff
        self.unitCostIntegral = _unitCostIntegral

    self.reapIntegralFor[_account] += self.balances[_account] * (_unitCostIntegral - self.lastUnitCostIntegralFor[_account]) / VOTE_DIVIDER / (block.timestamp - self.lastReapTimestampFor[_account])
    self.lastReapTimestampFor[_account] = block.timestamp
    self.lastUnitCostIntegralFor[_account] = _unitCostIntegral


@external
def deposit(_amount: uint256, _account: address = msg.sender, _feeOptimization: bool = False):
    assert _amount > 0, "amount must be greater 0"
    
    if _account != msg.sender:
        _allowance: uint256 = self.depositAllowance[_account][msg.sender]
        if _allowance != MAX_UINT256:
            self.depositAllowance[_account][msg.sender] = _allowance - _amount

    self._snapshot(_account)

    ERC20(self.lpToken).transferFrom(msg.sender, self, _amount)
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


@external
def invest():
    _amount: uint256 = ERC20(self.lpToken).balanceOf(self)
    if _amount > 0:
        ReaperStrategy(self.reaperStrategy).invest(_amount)


@external
def reap():
    ReaperStrategy(self.reaperStrategy).reap()


@external
def withdraw(_amount: uint256):
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


@external
def snapshot(_account: address = msg.sender):
    self._snapshot(_account)


@external
def setReaperStrategy(_reaperStrategy: address):
    assert msg.sender == self.owner, "owner only"
    ERC20(self.lpToken).approve(_reaperStrategy, MAX_UINT256)
    self.depositAllowance[self][_reaperStrategy] = MAX_UINT256
    self.reaperStrategy = _reaperStrategy


@external
def kill():
    assert msg.sender == self.owner, "owner only"
    self.isKilled = True


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
