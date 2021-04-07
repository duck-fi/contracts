def test_approve(strict_transferable_token, trinity, deployer):
    assert not strict_transferable_token.approve(
        trinity, 1_000, {'from': deployer}).return_value
    assert strict_transferable_token.allowance(deployer, trinity) == 0
