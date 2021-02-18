import pytest


def test_constructor(strict_transfable_token, white_list, deployer):
    assert strict_transfable_token.name() == "Strict Transfable Token"
    assert strict_transfable_token.symbol() == "STT"
    assert strict_transfable_token.decimals() == 18
    assert strict_transfable_token.totalSupply() == 0
    assert strict_transfable_token.balanceOf(
        deployer) == strict_transfable_token.totalSupply()
    assert strict_transfable_token.mintersCheckList() == white_list
    assert strict_transfable_token.transfableAccount() == deployer
