# @version ^0.2.11
"""
@title Controller Mock
@author Dispersion Finance Team
@license MIT
"""


import interfaces.Controller as Controller
import interfaces.VotingController as VotingController


implements: Controller


reapers: public(address[10 ** 3])
indexByReaper: public(HashMap[address, uint256])
lastReaperIndex: public(uint256)


@external
def __init__():
    pass


@view
@external
def farmToken() -> address:
    return ZERO_ADDRESS


@external
def startEmission(_votingController: address, _votingDelay: uint256):
    """
    @notice Start emission of `FarmToken`.
    @dev Callable by `owner` only. 
        Emits `YearEmissionUpdate(INITIAL_YEAR_EMISSION)` and `StartVoting(_votingDelay)` events
    @param _votingController Address of `VotingController` contract
    @param _votingDelay Initial delay defore next voting
    """
    VotingController(_votingController).startVoting(_votingDelay)


@external
@nonreentrant('lock')
def addReaper(_reaper: address):
    _reaperIndex: uint256 = self.indexByReaper[_reaper]
    assert _reaperIndex == 0, "reaper exists"

    _newReaperIndex: uint256 = self.lastReaperIndex + 1
    self.reapers[_newReaperIndex] = _reaper
    self.indexByReaper[_reaper] = _newReaperIndex
    self.lastReaperIndex = _newReaperIndex


@external
def removeReaper(_reaper: address):
    pass


@external
def claimAdminFee(_reaper: address, _gasToken: address = ZERO_ADDRESS):
    pass
