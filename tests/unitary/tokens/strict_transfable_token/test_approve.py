def test_approve(strict_transfable_token, trinity, deployer):
    assert not strict_transfable_token.approve(
        trinity, 1_000, {'from': deployer}).return_value
    assert strict_transfable_token.allowance(deployer, trinity) == 0
