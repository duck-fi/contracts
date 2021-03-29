# @version ^0.2.11
"""
@title Voting Controller Proxy
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.VotingController as VotingController


votingController: public(address)


@external
def __init__(_votingController: address):
    self.votingController = _votingController


@external
def vote(_reaper: address, _coin: address, _amount: uint256, _gasToken: address = ZERO_ADDRESS):
    ERC20(_coin).transferFrom(msg.sender, self, _amount)
    ERC20(_coin).approve(self.votingController, _amount)
    VotingController(self.votingController).vote(_reaper, _coin, _amount, _gasToken)
