# @version ^0.2.11
"""
@title Voting Controller
@author Dispersion Finance Team
@license MIT
"""

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.Controller as Controller
import interfaces.VotingController as VotingController
import interfaces.GasToken as GasToken
import interfaces.AddressesCheckList as AddressesCheckList


implements: Ownable
implements: VotingController


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

event StartVoting:
    delay: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


DAY: constant(uint256) = 86_400
WEEK: constant(uint256) = 7 * DAY
MULTIPLIER: constant(uint256) = 10 ** 18
INIT_VOTING_TIME: constant(uint256) = 1_609_372_800                                             # Thursday, 31 December 2020, 0:00:00 GMT
VOTING_PERIOD: constant(uint256) = WEEK
FARM_TOKEN_RATE: constant(uint256) = 1
VOTING_TOKEN_RATE: constant(uint256) = 2
VOTING_TOKEN_RATE_AMPLIFIER: constant(uint256) = 2
MIN_GAS_CONSTANT: constant(uint256) = 21_000


owner: public(address)
futureOwner: public(address)

farmToken: public(address)
votingToken: public(address)
controller: public(address)
gasTokenCheckList: public(address)
balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]])                 # reaper -> coin -> account -> amount
balancesUnlockTimestamp: public(HashMap[address, HashMap[address, HashMap[address, uint256]]])  # reaper -> coin -> account -> unlock timestamp
reaperBalances: public(HashMap[address, HashMap[address, uint256]])                             # reaper -> coin -> balance
lastVotes: public(HashMap[address, uint256])                                                    # reaper -> lastVotes
reaperIntegratedVotes: public(HashMap[address, uint256])                                        # reaper -> integrated votes
nextSnapshotTimestamp: public(uint256)
lastSnapshotTimestamp: public(uint256)
lastSnapshotIndex: public(uint256)
snapshots: public(VoteReaperSnapshot[MULTIPLIER][MULTIPLIER])                                   # [snapshot index, record index]
coinBalances: public(HashMap[address, uint256])                                                 # coin -> balance

votingTokenRate: public(uint256)
votingTokenRateAmplifier: public(uint256)


@external
def __init__(_controller: address, _gasTokenCheckList: address, _farmToken: address):
    """
    @notice Contract constructor
    @dev `_controller`, `_gasTokenCheckList`, `_farmToken` can't be equal `ZERO_ADDRESS`. `owner` = `msg.sender`
    @param _controller Address of Controller contract
    @param _gasTokenCheckList Address of AddressesCheckList contract with gas tokens allowed
    @param _farmToken Address of FarmToken contract (DSP)
    """
    assert _controller != ZERO_ADDRESS, "controller is not set"
    assert _gasTokenCheckList != ZERO_ADDRESS, "gasTokenCheckList is not set"
    assert _farmToken != ZERO_ADDRESS, "farmToken is not set"

    self.controller = _controller
    self.gasTokenCheckList = _gasTokenCheckList
    self.farmToken = _farmToken
    self.owner = msg.sender
    self.votingTokenRate = VOTING_TOKEN_RATE
    self.votingTokenRateAmplifier = VOTING_TOKEN_RATE_AMPLIFIER


@internal
def _reduceGas(_gasToken: address, _from: address, _gasStart: uint256, _callDataLength: uint256):
    """
    @notice Reduce gas function
    """
    if _gasToken == ZERO_ADDRESS:
        return

    assert AddressesCheckList(self.gasTokenCheckList).get(_gasToken), "unsupported gas token"
    gasSpent: uint256 = MIN_GAS_CONSTANT + _gasStart - msg.gas + 16 * _callDataLength
    GasToken(_gasToken).freeFromUpTo(_from, (gasSpent + 14154) / 41130)


@internal
def _snapshot():
    """
    @notice Makes a snapshot and fixes voting result per voting period, also updates historical reaper vote integrals
    @dev Only possible to call it once per voting period
    """
    if self.lastSnapshotTimestamp == 0 or block.timestamp < self.nextSnapshotTimestamp:
        return

    _controller: address = self.controller
    _lastReaperIndex: uint256 = Controller(_controller).lastReaperIndex()
    _lastSnapshotTimestamp: uint256 = self.lastSnapshotTimestamp

    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken
    _farmTokenBalance: uint256 = self.coinBalances[_farmToken]
    _votingTokenBalance: uint256 = self.coinBalances[_votingToken]
    if _farmTokenBalance + _votingTokenBalance == 0:
        return
    
    _votingTokenRate: uint256 = 0
    _totalVotePower: uint256 = 0

    if _farmTokenBalance + _votingTokenBalance > 0:
        _votingRate: uint256 = self.votingTokenRate
        _votingRateAmplifier: uint256 = self.votingTokenRateAmplifier
        _votingTokenRate = MULTIPLIER * _votingRate + MULTIPLIER * _votingRateAmplifier * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)
        _totalVotePower = _votingTokenBalance * _votingTokenRate / MULTIPLIER + _farmTokenBalance * FARM_TOKEN_RATE

    _currentSnapshotTimestamp: uint256 = INIT_VOTING_TIME + (block.timestamp - INIT_VOTING_TIME) / VOTING_PERIOD * VOTING_PERIOD
    _lastSnapshotIndex: uint256 = self.lastSnapshotIndex
    _dt: uint256 = _currentSnapshotTimestamp - _lastSnapshotTimestamp
    self.lastSnapshotTimestamp = _currentSnapshotTimestamp
    self.lastSnapshotIndex = _lastSnapshotIndex + 1
    self.nextSnapshotTimestamp = _currentSnapshotTimestamp + VOTING_PERIOD

    for i in range(1, MULTIPLIER):
        if i > _lastReaperIndex:
            break

        _currentReaper: address = Controller(_controller).reapers(i)
        _reaperVoteBalance: uint256 = 0

        if _totalVotePower == 0:
            self.snapshots[_lastSnapshotIndex + 1][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: 0, share: 0})
            self.reaperIntegratedVotes[_currentReaper] += self.lastVotes[_currentReaper] * _dt
            self.lastVotes[_currentReaper] = 0
        else:
            _reaperVoteBalance = self.reaperBalances[_currentReaper][_votingToken] * _votingTokenRate / MULTIPLIER + self.reaperBalances[_currentReaper][_farmToken] * FARM_TOKEN_RATE
            self.snapshots[_lastSnapshotIndex + 1][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: _reaperVoteBalance, share: _reaperVoteBalance * MULTIPLIER / _totalVotePower})
            self.reaperIntegratedVotes[_currentReaper] += self.lastVotes[_currentReaper] * _dt
            self.lastVotes[_currentReaper] = _reaperVoteBalance * MULTIPLIER / _totalVotePower


@external
@nonreentrant('lock')
def snapshot(_gasToken: address = ZERO_ADDRESS):
    _gasStart: uint256 = msg.gas
    self._snapshot()
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 1)


@external
@nonreentrant('lock')
def vote(_reaper: address, _coin: address, _amount: uint256, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Vote for reaper `_reaper` using tokens `_coin` with amount `_amount` for user `_account`
    @param _reaper Reaper to vote for
    @param _coin Coin which is used to vote
    @param _amount Amount which is used to vote
    @param _gasToken Gas token address (optional)
    """
    _gasStart: uint256 = msg.gas
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    assert _coin == self.farmToken or (_coin == self.votingToken and _coin != ZERO_ADDRESS), "invalid coin"
    self.balances[_reaper][_coin][msg.sender] += _amount
    self.balancesUnlockTimestamp[_reaper][_coin][msg.sender] = block.timestamp + VOTING_PERIOD
    self.reaperBalances[_reaper][_coin] += _amount
    self.coinBalances[_coin] += _amount
    assert ERC20(_coin).transferFrom(msg.sender, self, _amount)

    log Vote(_reaper, _coin, msg.sender, _amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 4)


@external
@nonreentrant('lock')
def unvote(_reaper: address, _coin: address, _amount: uint256, _gasToken: address = ZERO_ADDRESS):
    """
    @notice Unvote for reaper `_reaper` and withdraw tokens `_coin` with amount `_amount` for `_account`
    @dev Only possible with unlocked amount
    @param _reaper Reaper to unvote for
    @param _coin Coin which is used to unvote
    @param _amount Amount which is used to unvote
    @param _gasToken Gas token address (optional)
    """
    _gasStart: uint256 = msg.gas
    assert self.balancesUnlockTimestamp[_reaper][_coin][msg.sender] < block.timestamp, "tokens are locked"
    self.balances[_reaper][_coin][msg.sender] -= _amount
    self.reaperBalances[_reaper][_coin] -= _amount
    self.coinBalances[_coin] -= _amount
    assert ERC20(_coin).transfer(msg.sender, _amount)

    log Unvote(_reaper, _coin, msg.sender, _amount)
    self._reduceGas(_gasToken, msg.sender, _gasStart, 4 + 32 * 4)


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


@external
def voteIntegral(_reaper: address) -> uint256:
    """
    @notice Returns current vote integral for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote integral for
    @return Vote integral multiplied on 1e18
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"

    if block.timestamp > self.nextSnapshotTimestamp and self.lastSnapshotTimestamp > 0:
        self._snapshot()

    return self.reaperIntegratedVotes[_reaper] + self.lastVotes[_reaper] * (block.timestamp - self.lastSnapshotTimestamp)


@view
@external
def reaperVotePower(_reaper: address) -> uint256:
    """
    @notice Returns current vote power for reaper `_reaper`
    @param _reaper Reaper to get its vote power for
    @return Vote power
    """
    assert Controller(self.controller).indexByReaper(_reaper) > 0, "invalid reaper"
    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken
    _farmTokenBalance: uint256 = self.coinBalances[_farmToken]
    _votingTokenBalance: uint256 = self.coinBalances[_votingToken]

    if _farmTokenBalance + _votingTokenBalance == 0:
        return 0

    _votingRate: uint256 = self.votingTokenRate
    _votingRateAmplifier: uint256 = self.votingTokenRateAmplifier
    _votingTokenRate: uint256 = MULTIPLIER * _votingRate + MULTIPLIER * _votingRateAmplifier * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)
    return self.reaperBalances[_reaper][_votingToken] * _votingTokenRate / MULTIPLIER + self.reaperBalances[_reaper][_farmToken] * FARM_TOKEN_RATE


@view
@external
def totalVotePower() -> uint256:
    """
    @notice Returns current total vote power
    @return Vote power
    """
    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken
    _farmTokenBalance: uint256 = self.coinBalances[_farmToken]
    _votingTokenBalance: uint256 = self.coinBalances[_votingToken]

    if _farmTokenBalance + _votingTokenBalance == 0:
        return 0

    _votingRate: uint256 = self.votingTokenRate
    _votingRateAmplifier: uint256 = self.votingTokenRateAmplifier
    _votingTokenRate: uint256 = MULTIPLIER * _votingRate + MULTIPLIER * _votingRateAmplifier * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)
    return self.coinBalances[_votingToken] * _votingTokenRate / MULTIPLIER + self.coinBalances[_farmToken] * FARM_TOKEN_RATE


@view
@external
def accountVotePower(_reaper: address, _account: address) -> uint256:
    """
    @notice Returns vote power for account `_account` for reaper `_reaper`
    @param _reaper Reaper to get its vote power for
    @param _account Account to get its vote power for
    @return Vote power
    """
    _farmToken: address = self.farmToken
    _votingToken: address = self.votingToken

    if _votingToken == ZERO_ADDRESS:
        return self.balances[_reaper][_farmToken][_account] * FARM_TOKEN_RATE

    _farmTokenBalance: uint256 = self.coinBalances[_farmToken]
    _votingTokenBalance: uint256 = self.coinBalances[_votingToken]

    if _farmTokenBalance + _votingTokenBalance == 0:
        return 0

    _votingRate: uint256 = self.votingTokenRate
    _votingRateAmplifier: uint256 = self.votingTokenRateAmplifier
    _votingTokenRate: uint256 = MULTIPLIER * _votingRate + MULTIPLIER * _votingRateAmplifier * _farmTokenBalance / (_farmTokenBalance + _votingTokenBalance)
    return self.balances[_reaper][_votingToken][_account] * _votingTokenRate / MULTIPLIER + self.balances[_reaper][_farmToken][_account] * FARM_TOKEN_RATE


@external
def startVoting(_votingDelay: uint256 = 0):
    """
    @notice Unlock and start voting mechanism.
    @dev Callable once by `controller` only. Emit `StartVoting(_votingDelay)` event.
        Init equal distribution of votes (`1/REAPERS_COUNT`).
    @param _votingDelay Initial delay defore next voting
    """
    assert msg.sender == self.controller, "controller only"
    assert self.lastSnapshotTimestamp == 0, "already started"

    # initial voting round: we share equally for all reapers
    _controller: address = self.controller
    _lastReaperIndex: uint256 = Controller(_controller).lastReaperIndex()
    _totalVoteBalance: uint256 = _lastReaperIndex
    self.lastSnapshotTimestamp = block.timestamp
    self.nextSnapshotTimestamp = INIT_VOTING_TIME + (block.timestamp + VOTING_PERIOD + _votingDelay - INIT_VOTING_TIME) / VOTING_PERIOD * VOTING_PERIOD
    for i in range(1, MULTIPLIER):
        if i > _lastReaperIndex:
            break

        _currentReaper: address = Controller(_controller).reapers(i)
        _reaperShare: uint256 = MULTIPLIER / _totalVoteBalance
        self.snapshots[0][i] = VoteReaperSnapshot({reaper: _currentReaper, votes: 1, share: _reaperShare})
        self.lastVotes[_currentReaper] = _reaperShare
    
    log StartVoting(_votingDelay)


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


@external
def setVotingToken(_votingToken: address):
    """
    @notice Set voting token address.
    @dev Callable once by owner only. `_votingToken` can't be equal `ZERO_ADDRESS`.
    @param _votingToken New address of `StrictTransferableToken`(ERC20 for voting) contract
    """
    assert msg.sender == self.owner, "owner only"
    assert _votingToken != ZERO_ADDRESS, "zero address"
    assert self.votingToken == ZERO_ADDRESS, "set only once"
    self.votingToken = _votingToken


@external
def setVotingTokenRate(_rate: uint256, _amplifier: uint256):
    """
    @notice Set voting token rate and amplifier.
    @dev Callable by owner only. `_rate` and `_rate` should be greater `0`.
    """
    assert msg.sender == self.owner, "owner only"
    assert _rate > 0 and _amplifier > 0, "can't be equal zero"
    self.votingTokenRate = _rate
    self.votingTokenRateAmplifier = _amplifier
