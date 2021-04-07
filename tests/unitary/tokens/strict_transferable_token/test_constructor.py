import pytest


def test_constructor(strict_transferable_token, white_list, deployer):
    assert strict_transferable_token.name() == "Strict Transferable Token"
    assert strict_transferable_token.symbol() == "STT"
    assert strict_transferable_token.decimals() == 18
    assert strict_transferable_token.totalSupply() == 0
    assert strict_transferable_token.balanceOf(
        deployer) == strict_transferable_token.totalSupply()
    assert strict_transferable_token.mintersCheckList() == white_list
    assert strict_transferable_token.transferableAccountCheckList() == white_list
