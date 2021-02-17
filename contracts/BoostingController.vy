# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Controller as Controller
import interfaces.BoostingController as BoostingController
import interfaces.GasToken as GasToken
import interfaces.GasReducible as GasReducible


implements: Ownable
implements: BoostingController
implements: GasReducible


struct BoostInfo:
    targetAmount: uint256
    instantAmount: uint256
    warmupTime: uint256
    finishTime: uint256


event Boost:
    reaper: address
    coin: address
    account: address
    amount: uint256

event Unboost:
    reaper: address
    coin: address
    account: address
    amount: uint256

# # event VoteApproval:
# #     reaper: address
# #     coin: address
# #     ownerAccount: address
# #     voterAccount: address
# #     canVote: bool

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MULTIPLIER: constant(uint256) = 10 ** 18
MIN_GAS_CONSTANT: constant(uint256) = 21_000
DAY: constant(uint256) = 86_400
WEEK: constant(uint256) = 7 * DAY
BOOST_WEAKNESS: constant(uint256) = 5 * 10 ** 17


owner: public(address)
futureOwner: public(address)

controller: public(address)
farmToken: public(address)
farmTokenRate: public(uint256)
boostingToken: public(address)
boostingTokenRate: public(uint256)
boostingTokenRateAmplifier: public(uint256)

balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> amount

totalBoosts: public(uint256)
boostIntegral: public(uint256)
lastBoostTimestamp: public(uint256)

boosts: public(HashMap[address, BoostInfo]) # account -> boostInfo
boostIntegralFor: public(HashMap[address, uint256]) # account -> integrated votes
lastBoostTimestampFor: public(HashMap[address, uint256]) # account -> last boost timestamp

lockingPeriod: public(uint256)
warmupTime: public(uint256)

# # reaperBalances: public(HashMap[address, HashMap[address, uint256]]) # reaper -> coin -> balance
# # lastVotes: public(HashMap[address, uint256])  # reaper -> lastVotes
# # reaperIntegratedVotes: public(HashMap[address, uint256]) # reaper -> integrated votes
# # lastSnapshotTimestamp: public(uint256)
# # lastSnapshotIndex: public(uint256)
# # snapshots: public(VoteReaperSnapshot[MULTIPLIER][MULTIPLIER]) # [snapshot index, record index]
boostAllowance: public(HashMap[address, HashMap[address, HashMap[address, HashMap[address, bool]]]]) # reaper -> coin -> owner -> voter -> canBoost
gasTokens: public(HashMap[address, bool])


@external
def __init__(_controller: address, _farmToken: address, _boostingToken: address):
    """
    @notice Contract constructor
    """
    self.controller = _controller
    self.farmToken = _farmToken
    self.farmTokenRate = 1
    self.boostingToken = _boostingToken
    self.boostingTokenRate = 2
    self.boostingTokenRateAmplifier = 2
    self.warmupTime = 2 * WEEK
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert self.gasTokens[_gasToken], "unsupported gas token" 

    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@internal
def _calcAmount(pointA: uint256, pointB: uint256, tsA: uint256, tsB: uint256, t: uint256) -> uint256:
    assert tsB >= tsA, "reverted timestamps"
    
    if tsB == tsA:
        return 0

    delta: uint256 = 0

    if pointA > pointB:
        delta = pointA - pointB
    else:
        delta = pointB - pointA
    
    return t * delta / (tsB - tsA)


@internal
def _updateBoostIntegral(_reaper: address, _account: address, _amount: uint256, _lockTime: uint256):
    # update common intergal
    if self.lastBoostTimestamp > 0:
        self.boostIntegral = self.boostIntegral + self.totalBoosts * (block.timestamp - self.lastBoostTimestamp)
    self.totalBoosts += _amount
    self.lastBoostTimestamp = block.timestamp

    if self.boosts[_account].finishTime == 0:
        # 1. its initial lock
        self.boosts[_account].instantAmount = 0
        self.boosts[_account].targetAmount = _amount
        self.boosts[_account].warmupTime = block.timestamp + self.warmupTime
        self.boosts[_account].finishTime = block.timestamp + _lockTime
        self.lastBoostTimestampFor[_account] = block.timestamp

        pass # todo: maybe return
    elif self.boosts[_account].warmupTime > block.timestamp:
        # 2. its during warmup
        # need to calc user ascending integral and rebase amount, warmupTime, finishTime

        # 2.1 calc current user integral
        _instantAmount: uint256 = self._calcAmount(self.boosts[_account].instantAmount, self.boosts[_account].targetAmount, self.lastBoostTimestampFor[_account], self.boosts[_account].warmupTime, block.timestamp)
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (_instantAmount + self.boosts[_account].instantAmount) * (block.timestamp - self.lastBoostTimestampFor[_account]) / 2
        self.lastBoostTimestampFor[_account] = block.timestamp

        # 2.2 rebase amount, warmupTime, finishTime
        self.boosts[_account].targetAmount += _amount
        self.boosts[_account].instantAmount = _instantAmount
        self.boosts[_account].warmupTime = block.timestamp + self.warmupTime
        self.boosts[_account].finishTime = max(self.boosts[_account].warmupTime + _lockTime, self.boosts[_account].finishTime + _lockTime) # TOOD: or make from warmupTime only?

        pass # todo: maybe return
    elif self.boosts[_account].finishTime > block.timestamp:
        # 3. its during reduction
        # need to calc user ascending integral, user descending integral and rebase amount, warmupTime, finishTime
        
        # 3.1 need to calc user ascending integral (if not calculated yet)
        if self.lastBoostTimestampFor[_account] < self.boosts[_account].warmupTime:
            self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].instantAmount + self.boosts[_account].targetAmount) * (self.boosts[_account].warmupTime - self.lastBoostTimestampFor[_account]) / 2
            self.boosts[_account].instantAmount = self.boosts[_account].targetAmount
        
        # 3.2 need to calc user descending integral
        _instantAmount: uint256 = self._calcAmount(self.boosts[_account].instantAmount, self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER, self.lastBoostTimestampFor[_account], self.boosts[_account].warmupTime, block.timestamp)
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (_instantAmount + self.boosts[_account].instantAmount) * (block.timestamp - self.boosts[_account].warmupTime) / 2
        self.lastBoostTimestampFor[_account] = block.timestamp

        # 3.3 rebase amount, warmupTime, finishTime
        self.boosts[_account].targetAmount += _amount
        self.boosts[_account].instantAmount = _instantAmount
        self.boosts[_account].warmupTime = block.timestamp + self.warmupTime
        self.boosts[_account].finishTime = max(self.boosts[_account].warmupTime + _lockTime, self.boosts[_account].finishTime + _lockTime)

        pass # todo: maybe return
    else:
        # 4. its after reduction
        # need to calc user ascending integral, user descending integral, user const integral and rebase amount, warmupTime, finishTime
        
        # 4.1 need to calc user ascending integral (if not calculated yet)
        if self.lastBoostTimestampFor[_account] < self.boosts[_account].warmupTime:
            self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].instantAmount + self.boosts[_account].targetAmount) * (self.boosts[_account].warmupTime - self.lastBoostTimestampFor[_account]) / 2
            self.lastBoostTimestampFor[_account] = self.boosts[_account].warmupTime

        # 4.2 need to calc user descending integral (if not calculated yet)
        if self.lastBoostTimestampFor[_account] < self.boosts[_account].finishTime:
            self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + (self.boosts[_account].targetAmount + self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER) * (self.boosts[_account].finishTime - self.lastBoostTimestampFor[_account]) / 2
            self.lastBoostTimestampFor[_account] = self.boosts[_account].finishTime
            self.boosts[_account].instantAmount = self.boosts[_account].targetAmount * BOOST_WEAKNESS / MULTIPLIER

        # 4.3 need to calc user const integral
        self.boostIntegralFor[_account] = self.boostIntegralFor[_account] + self.boosts[_account].instantAmount * (block.timestamp - self.lastBoostTimestampFor[_account]) / 2
        self.lastBoostTimestampFor[_account] = block.timestamp

        # 4.4 rebase amount, warmupTime, finishTime
        self.boosts[_account].targetAmount += _amount
        self.boosts[_account].warmupTime = block.timestamp + self.warmupTime
        self.boosts[_account].finishTime = max(self.boosts[_account].warmupTime + _lockTime, self.boosts[_account].finishTime + _lockTime)

        pass

    pass


@external
@nonreentrant('lock')
def boost(_reaper: address, _coin: address, _amount: uint256, _lockTime: uint256, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Boost reward in reaper `_reaper` using tokens `_coin` with amount `_amount` for user `_account`
    @param _reaper Reaper to boost in
    @param _coin Coin which is used to boost
    @param _amount Amount which is used to boost
    @param _account Account who is being boosted
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    assert _amount > 0, "amount must be greater 0"
    assert _coin == self.farmToken or _coin == self.boostingToken, "invalid coin"
    # TODO: check _lockTime (assert self.boosts[_account].finishTime > self.boosts[_account].warmupTime, )

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.boostAllowance[_reaper][_coin][_account][msg.sender], "boosting approve required"

    self.balances[_reaper][_coin][_account] += _amount
    _tokenRate: uint256 = self.farmTokenRate
    
    if _coin == self.boostingToken:
        _tokenRate = self.boostingTokenRate

    # self.reaperBalances[_reaper][_coin] += _amount

    # self.boostIntegralFor[_reaper][_account] = self.boostIntegralFor[_reaper][_account] + _oldAmount * (block.timestamp - self.lastBoostTimestampFor[_reaper][_account])

    # self.lastBoostTimestampFor[_reaper][_account] = block.timestamp

    self._updateBoostIntegral(_reaper, _account, _amount * _tokenRate, _lockTime) # TODO make integrals

    ERC20(_coin).transferFrom(_account, self, _amount)

    log Boost(_reaper, _coin, _account, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 6)


# # @external
# # @nonreentrant('lock')
# # def unvote(_reaper: address, _coin: address, _amount: uint256, _account: address = msg.sender):
# #     """
# #     @notice Unvote for reaper `_reaper` and withdraw tokens `_coin` with amount `_amount` for `_account`
# #     @dev Only possible with unlocked amount
# #     @param _reaper Reaper to unvote for
# #     @param _coin Coin which is used to unvote
# #     @param _amount Amount which is used to unvote
# #     @param _account Account who is unvoting
# #     """
# #     assert _amount > 0, "amount should be > 0"

# #     if _account != msg.sender:
# #         assert self.voteAllowance[_reaper][_coin][_account][msg.sender], "voting approve required"

# #     _unvoteAmount: uint256 = 0
# #     if self.strategyByCoin[_coin] == ZERO_ADDRESS:
# #         assert self.balances[_reaper][_coin][_account] >=  _amount, "insufficiend funds"
# #         _unvoteAmount = _amount
# #     else:
# #         _availableAmount: uint256 = VotingStrategy(self.strategyByCoin[_coin]).availableToUnvote(_account, _amount)
# #         assert self.balances[_reaper][_coin][_account] >= _availableAmount, "insufficiend funds"
# #         assert _availableAmount > 0, "tokens are locked"
# #         _unvoteAmount = VotingStrategy(self.strategyByCoin[_coin]).unvote(_account, _amount)

# #     self.balances[_reaper][_coin][_account] -= _unvoteAmount
# #     self.reaperBalances[_reaper][_coin] -= _unvoteAmount
    
# #     ERC20(_coin).transfer(_account, _unvoteAmount)

# #     log Unvote(_reaper, _coin, _account, _unvoteAmount)


# # @view
# # @external
# # def availableToUnvote(_reaper: address, _coin: address, _account: address) -> uint256:
# #     """
# #     @notice Check for available withdrawal amount from reaper `_reaper` for tokens `_coin` for account `_account`
# #     @param _reaper Reaper to unvote for
# #     @param _coin Coin which is used to unvote
# #     @param _account Account who is unvoting
# #     @return Unlocked amount to withdraw
# #     """
# #     if self.strategyByCoin[_coin] == ZERO_ADDRESS:
# #         return self.balances[_reaper][_coin][_account]
# #     else:
# #         return VotingStrategy(self.strategyByCoin[_coin]).availableToUnvote(_account, self.balances[_reaper][_coin][_account])


# @view
# @external
# def boostIntegral(_account: address) -> uint256:
#     """
#     @notice Returns current boost integral for account `_account`
#     @param _account Account to get its boost integral for
#     @return Boost integral
#     """
#     # assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
#     return self.reaperIntegratedVotes[_reaper] + self.lastVotes[_reaper] * (block.timestamp - self.lastSnapshotTimestamp)



# # @view
# # @external
# # def accountVotePower(_reaper: address, _coin: address, _account: address) -> uint256:
# #     """
# #     @notice Returns vote power share for account `_account` for reaper `_reaper` multiplied on 1e18
# #     @param _reaper Reaper to get its vote power for
# #     @param _coin Coin which has been used to vote
# #     @param _account Account to get its vote power for
# #     @return Vote power multiplied on 1e18
# #     """
# #     if self.strategyByCoin[_coin] == ZERO_ADDRESS:
# #         return 0
    
# #     return VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.balances[_reaper][_coin][_account])


# # @external
# # def voteApprove(_reaper: address, _coin: address, _voter: address, _canVote: bool):
# #     """
# #     @notice Allows to perform votes and unvotes for reaper `_reaper` in tokens `_coin` for `_voter` instead of msg.sender by setting `_canVote` param
# #     @param _reaper Reaper to approve voting for
# #     @param _coin Coin which is used to approve voting
# #     @param _voter Account who can do voting or unvoting instead of msg.sender
# #     @param _canVote Possibility of voting or unvoting
# #     """
# #     self.voteAllowance[_reaper][_coin][msg.sender][_voter] = _canVote

# #     log VoteApproval(_reaper, _coin, msg.sender, _voter, _canVote)


@external
def setGasToken(_gasToken: address, _value: bool):
    assert msg.sender == self.owner, "owner only"
    assert _gasToken != ZERO_ADDRESS, "_gasToken is not set"
    
    self.gasTokens[_gasToken] = _value


@external
def transferOwnership(_futureOwner: address):
    """
    @notice Sets new future owner address
    @dev Callable by owner only
    @param _futureOwner New future owner address
    """
    assert msg.sender == self.owner, "owner only"

    self.futureOwner = _futureOwner
    log CommitOwnership(_futureOwner)


@external
def applyOwnership():
    """
    @notice Applies new future owner address as current owner
    @dev Callable by owner only
    """
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.futureOwner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)
