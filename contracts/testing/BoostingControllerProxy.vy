# @version ^0.2.11
"""
@title Boosting Controller Proxy
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20
import interfaces.BoostingController as BoostingController


boostingController: public(address)


@external
def __init__(_boostingController: address):
    self.boostingController = _boostingController


@external
def boost(_coin: address, _amount: uint256, _lockTime: uint256, _gasToken: address = ZERO_ADDRESS):
    ERC20(_coin).transferFrom(msg.sender, self, _amount)
    ERC20(_coin).approve(self.boostingController, _amount)
    BoostingController(self.boostingController).boost(_coin, _amount, _lockTime, _gasToken)
