# @version ^0.2.11
"""
@title Curve Minter Mock
@author Dispersion Finance Team
@license MIT
"""


from vyper.interfaces import ERC20


interface LiquidityGauge:
    def claimable_tokens(addr: address) -> uint256: nonpayable


rewardToken: public(address)
minted: public(HashMap[address, HashMap[address, uint256]])


@external
def __init__(_rewardToken: address):
    assert _rewardToken != ZERO_ADDRESS
    self.rewardToken = _rewardToken


@external
def mint(_gauge: address):
    _toMint: uint256 = LiquidityGauge(_gauge).claimable_tokens(msg.sender)
    # _toMint: uint256 = _availableAmount - self.minted[msg.sender][_gauge]
    self.minted[msg.sender][_gauge] += _toMint
    ERC20(self.rewardToken).transfer(msg.sender, _toMint)
