# @version ^0.2.0

from vyper.interfaces import ERC20
import interfaces.strategies.VotingStrategy as VotingStrategy


interface ReaperController:
    def reaper_by_index(reaper: address) -> uint256: view
    def last_reaper_index() -> uint256: view
    def reapers(index: uint256) -> address: view


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


MULTIPLIER: constant(uint256) = 10 ** 18

admin: public(address)
reaper_controller: public(address)
coins: public(HashMap[address, bool])
coinsArray: public(address[MULTIPLIER])
strategies: public(HashMap[address, address]) # coin -> voting strategy
balances: public(HashMap[address, HashMap[address, HashMap[address, uint256]]]) # reaper -> coin -> account -> amount
reaper_balances: public(HashMap[address, HashMap[address, uint256]]) # reaper -> coin -> balance
last_votes: public(HashMap[address, uint256])  # reaper -> last_votes
snapshots: public(VoteReaperSnapshot[MULTIPLIER][MULTIPLIER]) # [snapshot index, record index]
last_snapshot_index: public(uint256)
last_snapshot_block: public(uint256)
vote_allowances: public(HashMap[address, HashMap[address, HashMap[address, bool]]]) # reaper -> owner_account -> voting_account -> can_vote


@external
def __init__(_reaper_controller: address):
    """
    @notice Contract constructor
    """
    self.reaper_controller = _reaper_controller
    self.admin = msg.sender


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
def unvote(_reaper: address, _coin: address, _amount: uint256):
    """
    @notice Unvote for reaper `_reaper` and withdraw tokens `_coin` with amount `_amount` for `msg.sender`
    @dev Only possible with unlocked amount
    @param _reaper Reaper to unvote for
    @param _coin Coin which is used to unvote
    @param _amount Amount which is used to unvote
    @param _account Account who is unvoting
    """
    assert _amount > 0 and self.strategies[_coin] != ZERO_ADDRESS, "invalid params"

    available_amount: uint256 = VotingStrategy(self.strategies[_coin]).availableToUnvote(msg.sender, self.balances[_reaper][_coin][msg.sender]) # TODO: maybe unvote for smb, not for sender only
    assert available_amount >=  _amount, "token balance is locked" # TODO: maybe another message
    
    new_amount: uint256 = VotingStrategy(self.strategies[_coin]).unvote(msg.sender, _amount)
    self.balances[_reaper][_coin][msg.sender] -= new_amount
    self.reaper_balances[_reaper][_coin] -= new_amount

    log Unvote(_reaper, _coin, msg.sender, new_amount)


@external
def toggleApprove(_reaper: address, _owner_account: address, _voting_account: address):
    self.vote_allowances[_reaper][_owner_account][_voting_account] = not self.vote_allowances[_reaper][_owner_account][_voting_account]


@external
@nonreentrant('lock')
def snapshot():
    assert self.admin == msg.sender, "unauthorized"
    
    last_reaper_index: uint256 = ReaperController(self.reaper_controller).last_reaper_index()
    self.last_snapshot_index += 1
    self.last_snapshot_block = block.number
    totalVoteBalance: uint256 = 0

    for i in range(14):
        current_reaper: address = ReaperController(self.reaper_controller).reapers(i)
        reaperVoteBalance: uint256 = 0

        for _coin in self.coinsArray:
            reaperVoteBalance += VotingStrategy(self.strategies[_coin]).coinToVotes(self.reaper_balances[current_reaper][_coin])

        self.snapshots[self.last_snapshot_index][i] = VoteReaperSnapshot({reaper: current_reaper, votes: reaperVoteBalance, share: 0})
        totalVoteBalance += reaperVoteBalance

    for i in range(14):
        self.snapshots[self.last_snapshot_index][i].share = self.snapshots[self.last_snapshot_index][i].votes * MULTIPLIER / totalVoteBalance
        self.last_votes[self.snapshots[self.last_snapshot_index][i].reaper] = self.snapshots[self.last_snapshot_index][i].share


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
    return self.last_votes[_reaper]


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
    assert not self.coins[_coin] and _strategy != ZERO_ADDRESS, "coin is not initialized"
    
    self.strategies[_coin] = _strategy