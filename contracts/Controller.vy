# @version ^0.2.0


# import interfaces.ReaperController as ReaperController
import interfaces.Ownable as Ownable
import interfaces.Minter as Minter
# import interfaces.Reaper as Reaper


implements: Ownable
implements: Minter
# implements: ReaperController


event Minted:
    recipient: indexed(address)
    reaper: address
    minted: uint256

event CommitOwnership:
    admin: address

event ApplyOwnership:
    admin: address


MAX_REAPERS_COUNT: constant(uint256) = 10 ** 6


token: public(address)
reapers: public(address[MAX_REAPERS_COUNT])
index_by_reaper: public(HashMap[address, uint256])
last_reaper_index: public(uint256)
minted: public(HashMap[address, HashMap[address, uint256]])
allowance: public(HashMap[address, HashMap[address, bool]])

owner: public(address)
futureOwner: public(address)


@external
def __init__(_token: address):
    self.token = _token
    self.owner = msg.sender


# @external
# def toggleApprove(account: address):
#     self.allowance[account][msg.sender] = not self.allowance[account][msg.sender]


@external
@nonreentrant('lock')
def mintFor(reaper: address, account: address = msg.sender):
    pass
    # assert self.index_by_reaper[reaper] > 0, "reaper is not supported"

    # Reaper(reaper).snapshot(account)
    # total_mint: uint256 = Reaper(reaper).farm_integral_for(account)
    # to_mint: uint256 = total_mint - self.minted[reaper][account]

    # if to_mint != 0:
    #     Minter(self.minter).mint(account, to_mint)
    #     self.minted[reaper][account] = total_mint

    #     log Minted(account, reaper, total_mint)


# @external
# @nonreentrant('lock')
# def mintFor(reaper: address, account: address):
#     if self.allowance[msg.sender][account]:
#         self._mint_for(reaper, account)


# @external
# @nonreentrant('lock')
# def addReaper(reaper: address):
#     assert msg.sender == self.owner, "owner only"

#     reaper_index: uint256 = self.index_by_reaper[reaper]
#     assert reaper_index == 0, "reaper exists"

#     new_reaper_index: uint256 = self.last_reaper_index + 1
#     self.reapers[new_reaper_index] = reaper
#     self.index_by_reaper[reaper] = new_reaper_index
#     self.last_reaper_index = new_reaper_index


# @external
# @nonreentrant('lock')
# def removeReaper(reaper: address):
#     assert msg.sender == self.owner, "owner only"

#     reaper_index: uint256 = self.index_by_reaper[reaper]
#     assert reaper_index > 0, "reaper has not exist"

#     last_reaper_idx: uint256 = self.last_reaper_index
#     last_reaper: address = self.reapers[last_reaper_idx]

#     self.reapers[reaper_index] = last_reaper
#     self.index_by_reaper[last_reaper] = reaper_index
#     self.index_by_reaper[reaper] = 0
#     self.reapers[last_reaper_idx] = ZERO_ADDRESS
#     self.last_reaper_index = last_reaper_idx - 1


# @external
# @nonreentrant('lock')
# def setMinter(_minter: address):
#     assert msg.sender == self.owner, "owner only"
#     self.minter = _minter


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
