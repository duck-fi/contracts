# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Controller as Controller
import interfaces.VotingController as VotingController
import interfaces.GasToken as GasToken
import interfaces.GasReducible as GasReducible


implements: Ownable
implements: VotingController
implements: GasReducible


struct VoteReaperSnapshot:
    reaper: address
    votes: uint256
    share: uint256


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


DAY: constant(uint256) = 86_400
WEEK: constant(uint256) = 7 * DAY
MULTIPLIER: constant(uint256) = 10 ** 18
INIT_VOTING_TIME: constant(uint256) = 1_609_372_800 # Thursday, 31 December 2020, 0:00:00 GMT
VOTING_PERIOD: constant(uint256) = WEEK
FARM_TOKEN_RATE: constant(uint256) = 1
VOTING_TOKEN_RATE: constant(uint256) = 2
VOTING_TOKEN_RATE_AMPLIFIER: constant(uint256) = 2
MIN_GAS_CONSTANT: constant(uint256) = 21_000


owner: public(address)
futureOwner: public(address)

controller: public(address)
farmToken: public(address)
votingToken: public(address)
balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> amount
balancesUnlockTimestamp: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> unlock timestamp
reaperBalances: public(HashMap[address, HashMap[address, uint256]]) # reaper -> coin -> balance
lastVotes: public(HashMap[address, uint256])  # reaper -> lastVotes
reaperIntegratedVotes: public(HashMap[address, uint256]) # reaper -> integrated votes
lastSnapshotTimestamp: public(uint256)
lastSnapshotIndex: public(uint256)
snapshots: public(VoteReaperSnapshot[MULTIPLIER][MULTIPLIER]) # [snapshot index, record index]
voteAllowance: public(HashMap[address, HashMap[address, HashMap[address, HashMap[address, bool]]]]) # reaper -> coin -> owner -> voter -> canVote
gasTokens: public(HashMap[address, bool])


@external
def __init__(_controller: address, _farmToken: address, _votingToken: address):
    """
    @notice Contract constructor
    """
    assert _controller != ZERO_ADDRESS, "controller is not set"
    assert _farmToken != ZERO_ADDRESS, "farmToken is not set"
    assert _votingToken != ZERO_ADDRESS, "votingToken is not set"

    self.controller = _controller
    self.farmToken = _farmToken
    self.votingToken = _votingToken
    self.owner = msg.sender


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    if _gasToken == ZERO_ADDRESS:
        return

    assert self.gasTokens[_gasToken], "unsupported gas token" 

    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@external
@nonreentrant('lock')
def snapshot(_gasToken: address = ZERO_ADDRESS):
    """
    @notice Makes a snapshot and fixes voting result per voting period, also updates historical reaper vote integrals
    @dev Only possible to call it once per voting period
    """
    assert self.lastSnapshotTimestamp + VOTING_PERIOD < block.timestamp, "already snapshotted"

    _gasStart: uint256 = msg.gas
    
    _lastReaperIndex: uint256 = Controller(self.controller).lastReaperIndex()
    
    if self.lastSnapshotTimestamp == 0:
        # initial voting round: we share equally for all reapers
        _totalVoteBalance: uint256 = _lastReaperIndex
        self.lastSnapshotTimestamp = INIT_VOTING_TIME + (block.timestamp - INIT_VOTING_TIME) / VOTING_PERIOD * VOTING_PERIOD
        for i in range(1, MULTIPLIER):
            if i > _lastReaperIndex:
                break

            _currentReaper: address = Controller(self.controller).reapers(i)
            _reaperShare: uint256 = 1 * MULTIPLIER / _totalVoteBalance

            self.snapshots[self.lastSnapshotIndex][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: 1, share: _reaperShare})
            self.lastVotes[_currentReaper] = _reaperShare

        return

    _currentSnapshotTimestamp: uint256 = block.timestamp / VOTING_PERIOD * VOTING_PERIOD
    _dt: uint256 = _currentSnapshotTimestamp - self.lastSnapshotTimestamp
    self.lastSnapshotTimestamp = _currentSnapshotTimestamp
    self.lastSnapshotIndex += 1
    _totalVoteBalance: uint256 = 0

    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken

    _farmTokenBalance: uint256 = ERC20(_farmToken).balanceOf(self)
    _votingTokenBalance: uint256 = ERC20(_votingToken).balanceOf(self)

    for i in range(1, MULTIPLIER):
        if i > _lastReaperIndex:
            break

        _currentReaper: address = Controller(self.controller).reapers(i)
        _reaperVoteBalance: uint256 = 0

        if _farmTokenBalance + _votingTokenBalance > 0:
            _votingTokenRate: uint256 = MULTIPLIER * VOTING_TOKEN_RATE + MULTIPLIER * VOTING_TOKEN_RATE_AMPLIFIER * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)
            _reaperVoteBalance = self.reaperBalances[_currentReaper][_votingToken] * _votingTokenRate / MULTIPLIER + self.reaperBalances[_currentReaper][_farmToken] * FARM_TOKEN_RATE

        self.snapshots[self.lastSnapshotIndex][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: _reaperVoteBalance, share: 0})
        _totalVoteBalance += _reaperVoteBalance

    for i in range(1, MULTIPLIER):
        if i > _lastReaperIndex:
            break

        _reaperShare: uint256 = self.snapshots[self.lastSnapshotIndex][i].votes * MULTIPLIER / _totalVoteBalance
        self.snapshots[self.lastSnapshotIndex][i].share = _reaperShare
        self.reaperIntegratedVotes[self.snapshots[self.lastSnapshotIndex][i].reaper] += self.lastVotes[self.snapshots[self.lastSnapshotIndex][i].reaper] * _dt
        self.lastVotes[self.snapshots[self.lastSnapshotIndex][i].reaper] = _reaperShare
    
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 1)


@external
@nonreentrant('lock')
def vote(_reaper: address, _coin: address, _amount: uint256, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Vote for reaper `_reaper` using tokens `_coin` with amount `_amount` for user `_account`
    @param _reaper Reaper to vote for
    @param _coin Coin which is used to vote
    @param _amount Amount which is used to vote
    @param _account Account who is voting
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    assert _amount > 0, "amount must be greater 0"
    assert _coin == self.farmToken or _coin == self.votingToken, "invalid coin"

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.voteAllowance[_reaper][_coin][_account][msg.sender], "voting approve required"

    self.balances[_reaper][_coin][_account] += _amount
    self.balancesUnlockTimestamp[_reaper][_coin][_account] = block.timestamp + VOTING_PERIOD
    self.reaperBalances[_reaper][_coin] += _amount
    
    ERC20(_coin).transferFrom(_account, self, _amount)

    log Vote(_reaper, _coin, _account, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 5)


@external
@nonreentrant('lock')
def unvote(_reaper: address, _coin: address, _amount: uint256, _account: address = msg.sender, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Unvote for reaper `_reaper` and withdraw tokens `_coin` with amount `_amount` for `_account`
    @dev Only possible with unlocked amount
    @param _reaper Reaper to unvote for
    @param _coin Coin which is used to unvote
    @param _amount Amount which is used to unvote
    @param _account Account who is unvoting
    """
    assert _amount > 0, "amount should be > 0"

    _gasStart: uint256 = msg.gas

    if _account != msg.sender:
        assert self.voteAllowance[_reaper][_coin][_account][msg.sender], "voting approve required"

    assert self.balances[_reaper][_coin][_account] >= _amount, "insufficiend funds"
    assert self.balancesUnlockTimestamp[_reaper][_coin][_account] < block.timestamp, "tokens are locked"

    self.balances[_reaper][_coin][_account] -= _amount
    self.reaperBalances[_reaper][_coin] -= _amount
    
    ERC20(_coin).transfer(_account, _amount)

    log Unvote(_reaper, _coin, _account, _amount)

    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 5)


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
    if self.balancesUnlockTimestamp[_reaper][_coin][_account] >= block.timestamp:
        return 0
    
    return self.balances[_reaper][_coin][_account]


@view
@external
def voteIntegral(_reaper: address) -> uint256:
    """
    @notice Returns current vote integral for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote integral for
    @return Vote integral multiplied on 1e18
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    return self.reaperIntegratedVotes[_reaper] + self.lastVotes[_reaper] * (block.timestamp - self.lastSnapshotTimestamp)


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

    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken

    _farmTokenBalance: uint256 = ERC20(_farmToken).balanceOf(self)
    _votingTokenBalance: uint256 = ERC20(_votingToken).balanceOf(self)

    for i in range(1, MULTIPLIER):
        if i > _lastReaperIndex:
            break

        _currentReaper: address = Controller(self.controller).reapers(i)
        _reaperVoteBalance: uint256 = 0

        if _farmTokenBalance + _votingTokenBalance > 0:
            _votingTokenRate: uint256 = MULTIPLIER * VOTING_TOKEN_RATE + MULTIPLIER * VOTING_TOKEN_RATE_AMPLIFIER * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)
            _reaperVoteBalance = self.reaperBalances[_currentReaper][_votingToken] * _votingTokenRate / MULTIPLIER + self.reaperBalances[_currentReaper][_farmToken] * FARM_TOKEN_RATE

        if _reaper == _currentReaper:
            _targetVoteBalance = _reaperVoteBalance

        _totalVoteBalance += _reaperVoteBalance

    if _totalVoteBalance > 0:
        return _targetVoteBalance * MULTIPLIER / _totalVoteBalance

    return 0


@view
@external
def accountVotePower(_reaper: address, _account: address) -> uint256:
    """
    @notice Returns vote power share for account `_account` for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote power for
    @param _account Account to get its vote power for
    @return Vote power multiplied on 1e18
    """
    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken

    _farmTokenBalance: uint256 = ERC20(_farmToken).balanceOf(self)
    _votingTokenBalance: uint256 = ERC20(_votingToken).balanceOf(self)

    if _farmTokenBalance + _votingTokenBalance == 0:
        return 0

    _votingTokenRate: uint256 = MULTIPLIER * VOTING_TOKEN_RATE + MULTIPLIER * VOTING_TOKEN_RATE_AMPLIFIER * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)

    return self.balances[_reaper][self.votingToken][_account] * _votingTokenRate / MULTIPLIER + self.balances[_reaper][self.farmToken][_account] * FARM_TOKEN_RATE


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
