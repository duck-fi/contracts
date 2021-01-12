# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.Ownable as Ownable
import interfaces.strategies.VotingStrategy as VotingStrategy


interface ReaperController:
    def reaper_by_index(reaper: address) -> uint256: view
    def last_reaper_index() -> uint256: view
    def reapers(index: uint256) -> address: view


implements: Ownable


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

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MULTIPLIER: constant(uint256) = 10 ** 18
WEEK: constant(uint256) = 604800
INIT_VOTING_TIME: constant(uint256) = 1609372800 # Thursday, 31 December 2020, 0:00:00 GMT

owner: public(address)
future_owner: public(address)
admin: public(address)
reaper_controller: public(address)
coins: public(HashMap[address, bool])
coinsArray: public(address[MULTIPLIER])
strategies: public(HashMap[address, address]) # coin -> voting strategy
balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> amount
reaper_balances: public(HashMap[address, HashMap[address, uint256]]) # reaper -> coin -> balance
current_votes: public(HashMap[address, uint256])  # reaper -> current_votes
voting_period: public(uint256)
reaper_integrated_votes: public(HashMap[address, uint256]) # reaper -> integrated_votes
last_snapshot_timestamp: public(uint256)
last_snapshot_index: public(uint256)
snapshots: public(VoteReaperSnapshot[MULTIPLIER][MULTIPLIER]) # [snapshot index, record index]
vote_allowances: public(HashMap[address, HashMap[address, HashMap[address, bool]]]) # reaper -> owner_account -> voting_account -> can_vote


@external
def __init__(_reaper_controller: address):
    """
    @notice Contract constructor
    """
    self.reaper_controller = _reaper_controller
    self.voting_period = WEEK
    self.admin = msg.sender
    self.owner = msg.sender


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
    assert ReaperController(self.reaper_controller).reaper_by_index(_reaper) > 0, "invalid reaper"
    assert self.coins[_coin] and _amount > 0 and self.strategies[_coin] != ZERO_ADDRESS, "invalid params"
    if _account != msg.sender:
        assert self.vote_allowances[_reaper][_account][msg.sender], "voting approve required"
    assert ERC20(_account).balanceOf(_coin) >= _amount, "insufficient funds"
    assert ERC20(_account).transferFrom(_account, self, _amount), "approve required"

    new_amount: uint256 = VotingStrategy(self.strategies[_coin]).vote(_account, _amount)

    self.balances[_reaper][_coin][_account] += new_amount
    self.reaper_balances[_reaper][_coin] += new_amount

    log Vote(_reaper, _coin, _account, new_amount)


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
    assert _amount > 0 and self.strategies[_coin] != ZERO_ADDRESS, "invalid params"
    
    if _account != msg.sender:
        assert self.vote_allowances[_reaper][_account][msg.sender], "voting approve required"

    available_amount: uint256 = VotingStrategy(self.strategies[_coin]).availableToUnvote(_account, self.balances[_reaper][_coin][_account])
    assert available_amount >=  _amount, "token balance is locked" # TODO: maybe another message
    
    new_amount: uint256 = VotingStrategy(self.strategies[_coin]).unvote(_account, _amount)
    self.balances[_reaper][_coin][_account] -= new_amount
    self.reaper_balances[_reaper][_coin] -= new_amount

    log Unvote(_reaper, _coin, _account, new_amount)


@external
def toggleApprove(_reaper: address, _owner_account: address, _voting_account: address):
    self.vote_allowances[_reaper][_owner_account][_voting_account] = not self.vote_allowances[_reaper][_owner_account][_voting_account]


@external
@nonreentrant('lock')
def snapshot():
    assert self.admin == msg.sender, "unauthorized"
    assert self.last_snapshot_timestamp + self.voting_period < block.timestamp, "already snapshotted"
    
    last_reaper_index: uint256 = ReaperController(self.reaper_controller).last_reaper_index()
    
    if self.last_snapshot_timestamp == 0:
        # initial voting round: we share equally for all reapers
        totalVoteBalance: uint256 = last_reaper_index + 1
        self.last_snapshot_timestamp = INIT_VOTING_TIME + (block.timestamp - INIT_VOTING_TIME) / self.voting_period * self.voting_period
        for i in range(1, MULTIPLIER):
            if i > last_reaper_index:
                break

            current_reaper: address = ReaperController(self.reaper_controller).reapers(i)
            reaper_share: uint256 = 1 * MULTIPLIER / totalVoteBalance

            self.snapshots[self.last_snapshot_index][i] = VoteReaperSnapshot({reaper: current_reaper, votes: 1, share: reaper_share})
            self.current_votes[current_reaper] = reaper_share

        return

    current_snapshot_timestamp: uint256 = block.timestamp / self.voting_period * self.voting_period
    dt: uint256 = current_snapshot_timestamp - self.last_snapshot_timestamp
    self.last_snapshot_timestamp = current_snapshot_timestamp
    self.last_snapshot_index += 1
    totalVoteBalance: uint256 = 0

    for i in range(1, MULTIPLIER):
        if i > last_reaper_index:
            break

        current_reaper: address = ReaperController(self.reaper_controller).reapers(i)
        reaperVoteBalance: uint256 = 0

        for _coin in self.coinsArray:
            reaperVoteBalance += VotingStrategy(self.strategies[_coin]).coinToVotes(self.reaper_balances[current_reaper][_coin])

        self.snapshots[self.last_snapshot_index][i] = VoteReaperSnapshot({reaper: current_reaper, votes: reaperVoteBalance, share: 0})
        totalVoteBalance += reaperVoteBalance

    for i in range(1, MULTIPLIER):
        if i > last_reaper_index:
            break

        reaper_share: uint256 = self.snapshots[self.last_snapshot_index][i].votes * MULTIPLIER / totalVoteBalance
        self.snapshots[self.last_snapshot_index][i].share = reaper_share
        self.reaper_integrated_votes[self.snapshots[self.last_snapshot_index][i].reaper] += self.current_votes[self.snapshots[self.last_snapshot_index][i].reaper] * dt
        self.current_votes[self.snapshots[self.last_snapshot_index][i].reaper] = reaper_share


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
    return VotingStrategy(self.strategies[_coin]).availableToUnvote(_account, self.balances[_reaper][_coin][_account])


@view
@external
def reaperVotePower(_reaper: address) -> uint256:
    """
    @notice Returns vote power share for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote power for
    @return Vote power multiplied on 1e18
    """
    return self.current_votes[_reaper]


@view
@external
def accountVotePower(_reaper: address, _coin: address, _account: address) -> uint256:
    """
    @notice Returns vote power share for account `_account` for reaper `_reaper` multiplied on 1e18
    @param _reaper Reaper to get its vote power for
    @param _account Coin which has been used to vote
    @param _account Account to get its vote power for
    @return Vote power multiplied on 1e18
    """
    return VotingStrategy(self.strategies[_coin]).coinToVotes(self.balances[_reaper][_coin][_account])


@external
def setStrategy(_coin: address, _strategy: address = ZERO_ADDRESS):
    """
    @notice Sets or removes strategy `_strategy` for coin `_coin`
    @param _coin Coin to set or remove strategy for
    @param _strategy Strategy contract address (ZERO_ADDRESS to remove)
    """
    assert self.owner == msg.sender, "unauthorized"
    assert not self.coins[_coin] and _strategy != ZERO_ADDRESS, "coin is not initialized"
    
    self.strategies[_coin] = _strategy


@external
def setVotingPeriod(_period: uint256):
    assert self.owner == msg.sender, "unauthorized"
    assert _period > 0, "invalid params"

    self.voting_period = _period


@external
def setAdmin(_admin: address):
    assert self.owner == msg.sender, "unauthorized"
    assert _admin != ZERO_ADDRESS, "invalid params"

    self.admin = _admin


@external
def transferOwnership(_future_owner: address):
    assert msg.sender == self.owner, "owner only"

    self.future_owner = _future_owner
    log CommitOwnership(_future_owner)


@external
def applyOwnership():
    assert msg.sender == self.owner, "owner only"
    _owner: address = self.future_owner
    assert _owner != ZERO_ADDRESS, "owner not set"
    self.owner = _owner
    log ApplyOwnership(_owner)