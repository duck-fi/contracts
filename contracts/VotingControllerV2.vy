# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Controller as Controller
import interfaces.VotingController as VotingController
import interfaces.strategies.VotingStrategy as VotingStrategy


implements: Ownable
# implements: VotingController TODO


event Vote:
    reaper: address
    coin: address
    account: address
    amount: uint256

event Unvote:
    reaper: address
    coin: address
    account: address
    amount: uint256

event VoteApproval:
    reaper: address
    coin: address
    ownerAccount: address
    voterAccount: address
    canVote: bool

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MULTIPLIER: constant(uint256) = 10 ** 18
WEEK: constant(uint256) = 604800
INIT_VOTING_TIME: constant(uint256) = 1609372800 # Thursday, 31 December 2020, 0:00:00 GMT

owner: public(address)
futureOwner: public(address)

controller: public(address)
coins: public(address[MULTIPLIER])
lastCoinIndex: public(uint256)
indexByCoin: public(HashMap[address, uint256]) # coin -> index
strategyByCoin: public(HashMap[address, address]) # coin -> voting strategy
balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> amount
reaperBalances: public(HashMap[address, HashMap[address, uint256]]) # reaper -> coin -> balance
totalBalances: public(HashMap[address, uint256]) # coin -> balance
reaperVotes: public(HashMap[address, uint256]) # reaper -> reaper votes
totalVotes: public(uint256)
totalIntegratedVotes: public(uint256)
reaperIntegratedVotes: public(HashMap[address, uint256]) # reaper -> integrated votes
lastReaperIntegratedTimestamp:  public(HashMap[address, uint256]) # reaper -> integrated votes timestamp
lastTotalIntegratedTimestamp: public(uint256)

voteAllowance: public(HashMap[address, HashMap[address, HashMap[address, HashMap[address, bool]]]]) # reaper -> coin -> owner -> voter -> canVote


@external
def __init__(_controller: address):
    """
    @notice Contract constructor
    """
    self.controller = _controller
    self.owner = msg.sender


# @external
# @nonreentrant('lock')
# def snapshot():
#     """
#     @notice Makes a snapshot and fixes voting result per voting period, also updates historical reaper vote integrals
#     @dev Only possible to call it once per voting period
#     """
#     assert self.lastSnapshotTimestamp + self.votingPeriod < block.timestamp, "already snapshotted"
    
#     _lastReaperIndex: uint256 = Controller(self.controller).lastReaperIndex()
    
#     if self.lastSnapshotTimestamp == 0:
#         # initial voting round: we share equally for all reapers
#         _totalVoteBalance: uint256 = _lastReaperIndex
#         self.lastSnapshotTimestamp = INIT_VOTING_TIME + (block.timestamp - INIT_VOTING_TIME) / self.votingPeriod * self.votingPeriod
#         for i in range(1, MULTIPLIER):
#             if i > _lastReaperIndex:
#                 break

#             _currentReaper: address = Controller(self.controller).reapers(i)
#             _reaperShare: uint256 = 1 * MULTIPLIER / _totalVoteBalance

#             self.snapshots[self.lastSnapshotIndex][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: 1, share: _reaperShare})
#             self.lastVotes[_currentReaper] = _reaperShare

#         return

#     _currentSnapshotTimestamp: uint256 = block.timestamp / self.votingPeriod * self.votingPeriod
#     _dt: uint256 = _currentSnapshotTimestamp - self.lastSnapshotTimestamp
#     self.lastSnapshotTimestamp = _currentSnapshotTimestamp
#     self.lastSnapshotIndex += 1
#     _totalVoteBalance: uint256 = 0

#     for i in range(1, MULTIPLIER):
#         if i > _lastReaperIndex:
#             break

#         _currentReaper: address = Controller(self.controller).reapers(i)
#         _reaperVoteBalance: uint256 = 0

#         for j in range(1, MULTIPLIER):
#             if j > self.lastCoinIndex:
#                 break

#             _coin: address = self.coins[j]
#             _reaperVoteBalance += VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.reaperBalances[_currentReaper][_coin])

#         self.snapshots[self.lastSnapshotIndex][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: _reaperVoteBalance, share: 0})
#         _totalVoteBalance += _reaperVoteBalance

#     for i in range(1, MULTIPLIER):
#         if i > _lastReaperIndex:
#             break

#         _reaperShare: uint256 = self.snapshots[self.lastSnapshotIndex][i].votes * MULTIPLIER / _totalVoteBalance
#         self.snapshots[self.lastSnapshotIndex][i].share = _reaperShare
#         self.reaperIntegratedVotes[self.snapshots[self.lastSnapshotIndex][i].reaper] += self.lastVotes[self.snapshots[self.lastSnapshotIndex][i].reaper] * _dt
#         self.lastVotes[self.snapshots[self.lastSnapshotIndex][i].reaper] = _reaperShare
@internal
def _updateReaperIntegral(_reaper: address):
    _reaperVoteBalance: uint256 = 0
    _totalVoteBalance: uint256 = 0

    for j in range(1, MULTIPLIER):
        if j > self.lastCoinIndex:
            break

        _coin: address = self.coins[j]
        _reaperVoteBalance += VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.reaperBalances[_reaper][_coin])
        _totalVoteBalance += VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.totalBalances[_coin])

    self.reaperIntegratedVotes[_reaper] = self.reaperIntegratedVotes[_reaper] + self.reaperVotes[_reaper] * (block.timestamp - self.lastReaperIntegratedTimestamp[_reaper])
    self.totalIntegratedVotes = self.totalIntegratedVotes + self.totalVotes * (block.timestamp - self.lastTotalIntegratedTimestamp)

    self.reaperVotes[_reaper] = _reaperVoteBalance
    self.totalVotes = _totalVoteBalance
    self.lastReaperIntegratedTimestamp[_reaper] = block.timestamp
    self.lastTotalIntegratedTimestamp = block.timestamp


@external
@nonreentrant('lock')
def vote(_reaper: address, _coin: address, _amount: uint256, _account: address = msg.sender):
    """
    @notice Vote for reaper `_reaper` using tokens `_coin` with amount `_amount` for user `_account`
    @param _reaper Reaper to vote for
    @param _coin Coin which is used to vote
    @param _amount Amount which is used to vote
    @param _account Account who is voting
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    assert _amount > 0, "amount must be greater 0"
    assert self.indexByCoin[_coin] > 0 and self.strategyByCoin[_coin] != ZERO_ADDRESS, "invalid coin"

    if _account != msg.sender:
        assert self.voteAllowance[_reaper][_coin][_account][msg.sender], "voting approve required"
    
    ERC20(_coin).transferFrom(_account, self, _amount)

    _availableAmount: uint256 = VotingStrategy(self.strategyByCoin[_coin]).availableToVote(_account, _amount)
    VotingStrategy(self.strategyByCoin[_coin]).vote(_account, _amount)
    
    self.balances[_reaper][_coin][_account] += _availableAmount
    self.reaperBalances[_reaper][_coin] += _availableAmount
    self.totalBalances[_coin] += _availableAmount

    if _amount - _availableAmount > 0:
        self.balances[_reaper][_coin][self] += _amount - _availableAmount

    self._updateReaperIntegral(_reaper)

    log Vote(_reaper, _coin, _account, _availableAmount)


@external
@nonreentrant('lock')
def unvote(_reaper: address, _coin: address, _amount: uint256, _account: address = msg.sender):
    """
    @notice Unvote for reaper `_reaper` and withdraw tokens `_coin` with amount `_amount` for `_account`
    @dev Only possible with unlocked amount
    @param _reaper Reaper to unvote for
    @param _coin Coin which is used to unvote
    @param _amount Amount which is used to unvote
    @param _account Account who is unvoting
    """
    assert _amount > 0, "amount should be > 0"

    if _account != msg.sender:
        assert self.voteAllowance[_reaper][_coin][_account][msg.sender], "voting approve required"

    _unvoteAmount: uint256 = 0
    if self.strategyByCoin[_coin] == ZERO_ADDRESS:
        assert self.balances[_reaper][_coin][_account] >=  _amount, "insufficiend funds"
        _unvoteAmount = _amount
    else:
        _availableAmount: uint256 = VotingStrategy(self.strategyByCoin[_coin]).availableToUnvote(_account, _amount)
        assert self.balances[_reaper][_coin][_account] >= _availableAmount, "insufficiend funds"
        assert _availableAmount > 0, "tokens are locked"
        _unvoteAmount = VotingStrategy(self.strategyByCoin[_coin]).unvote(_account, _amount)

    self.balances[_reaper][_coin][_account] -= _unvoteAmount
    self.reaperBalances[_reaper][_coin] -= _unvoteAmount
    self.totalBalances[_coin] -= _unvoteAmount
    
    ERC20(_coin).transfer(_account, _unvoteAmount)

    self._updateReaperIntegral(_reaper)

    log Unvote(_reaper, _coin, _account, _unvoteAmount)


@view
@external
def availableToUnvote(_reaper: address, _coin: address, _account: address) -> uint256:
    """
    @notice Check for available withdrawal amount from reaper `_reaper` for tokens `_coin` for account `_account`
    @param _reaper Reaper to unvote for
    @param _coin Coin which is used to unvote
    @param _account Account who is unvoting
    @return Unlocked amount to withdraw
    """
    if self.strategyByCoin[_coin] == ZERO_ADDRESS:
        return self.balances[_reaper][_coin][_account]
    else:
        return VotingStrategy(self.strategyByCoin[_coin]).availableToUnvote(_account, self.balances[_reaper][_coin][_account])


@view
@external
def voteIntegral(_reaper: address) -> uint256:
    """
    @notice Returns current vote integral for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote integral for
    @return Vote integral multiplied on 1e18
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"

    reaperIntegral: uint256 = self.reaperIntegratedVotes[_reaper] + self.reaperVotes[_reaper] * (block.timestamp - self.lastReaperIntegratedTimestamp[_reaper])
    totalIntegral: uint256 = self.totalIntegratedVotes + self.totalVotes * (block.timestamp - self.lastTotalIntegratedTimestamp)

    return reaperIntegral * MULTIPLIER / totalIntegral


@view
@external
def reaperVotePower(_reaper: address) -> uint256:
    """
    @notice Returns current vote power share for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote power for
    @return Vote power multiplied on 1e18
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"

    _lastReaperIndex: uint256 = Controller(self.controller).lastReaperIndex()
    _totalVoteBalance: uint256 = 0
    _targetVoteBalance: uint256 = 0

    for i in range(1, MULTIPLIER):
        if i > _lastReaperIndex:
            break

        _currentReaper: address = Controller(self.controller).reapers(i)
        _reaperVoteBalance: uint256 = 0

        for j in range(1, MULTIPLIER):
            if j > self.lastCoinIndex:
                break

            _coin: address = self.coins[j]
            _reaperVoteBalance += VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.reaperBalances[_currentReaper][_coin])

        if _reaper == _currentReaper:
            _targetVoteBalance = _reaperVoteBalance

        _totalVoteBalance += _reaperVoteBalance

    if _totalVoteBalance > 0:
        return _targetVoteBalance * MULTIPLIER / _totalVoteBalance

    return 0


@view
@external
def accountVotePower(_reaper: address, _coin: address, _account: address) -> uint256:
    """
    @notice Returns vote power share for account `_account` for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote power for
    @param _coin Coin which has been used to vote
    @param _account Account to get its vote power for
    @return Vote power multiplied on 1e18
    """
    if self.strategyByCoin[_coin] == ZERO_ADDRESS:
        return 0
    
    return VotingStrategy(self.strategyByCoin[_coin]).coinToVotes(self.balances[_reaper][_coin][_account])


@external
def voteApprove(_reaper: address, _coin: address, _voter: address, _canVote: bool):
    """
    @notice Allows to perform votes and unvotes for reaper `_reaper` in tokens `_coin` for `_voter` instead of msg.sender by setting `_canVote` param
    @param _reaper Reaper to approve voting for
    @param _coin Coin which is used to approve voting
    @param _voter Account who can do voting or unvoting instead of msg.sender
    @param _canVote Possibility of voting or unvoting
    """
    self.voteAllowance[_reaper][_coin][msg.sender][_voter] = _canVote

    log VoteApproval(_reaper, _coin, msg.sender, _voter, _canVote)


@external
def setVotingStrategy(_coin: address, _votingStrategy: address = ZERO_ADDRESS):
    """
    @notice Sets or removes strategy `_votingStrategy` for coin `_coin`
    @dev Callable by owner only
    @param _coin Coin to set or remove strategy for
    @param _votingStrategy Strategy contract address (ZERO_ADDRESS to remove)
    """
    assert self.owner == msg.sender, "owner only"

    if self.indexByCoin[_coin] == 0:
        # new coin addition with strategy
        assert _votingStrategy != ZERO_ADDRESS, "invalid strategy"

        _newCoinIndex: uint256 = self.lastCoinIndex + 1
        self.coins[_newCoinIndex] = _coin
        self.indexByCoin[_coin] = _newCoinIndex
        self.lastCoinIndex = _newCoinIndex
    elif _votingStrategy == ZERO_ADDRESS:
        # removing coin and strategy
        _removingCoinIndex: uint256 = self.indexByCoin[_coin]
        _lastCoinIndex: uint256 = self.lastCoinIndex
        
        if _removingCoinIndex < _lastCoinIndex:
            self.indexByCoin[_coin] = 0
            last_coin: address = self.coins[_lastCoinIndex]
            self.coins[_lastCoinIndex] = ZERO_ADDRESS
            self.indexByCoin[last_coin] = _removingCoinIndex
            self.coins[_removingCoinIndex] = last_coin
        else:
            self.coins[_lastCoinIndex] = ZERO_ADDRESS
        
        self.indexByCoin[_coin] = 0
        self.lastCoinIndex -= 1
    
    # updating strategy
    self.strategyByCoin[_coin] = _votingStrategy


# @external
# def setVotingPeriod(_votingPeriod: uint256):
#     """
#     @notice Sets voting period `_votingPeriod` in unixtime
#     @dev Callable by owner only
#     @param _votingPeriod Voting period in unixtime
#     """
#     assert self.owner == msg.sender, "owner only"
#     assert _votingPeriod > 0, "invalid params"

#     self.votingPeriod = _votingPeriod


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
