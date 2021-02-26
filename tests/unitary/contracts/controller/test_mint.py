import brownie

def test_mint(controller, reaper_mock, lp_token, farm_token, ZERO_ADDRESS, neo, morpheus, exception_tester, week):
    controller.addReaper(reaper_mock, {'from': neo})
    farm_token.setMinter(controller, {'from': neo})
    farm_token.startEmission({'from': neo})

    lp_token.transfer(morpheus, 100, {'from': neo})
    lp_token.approve(reaper_mock, 100, {'from': morpheus})

    brownie.chain.mine(1, brownie.chain.time() + 1)
    reaper_mock.deposit(100, {'from': morpheus})
    block_timestamp_1 = brownie.chain.time()
    initial_balance_morpheus_1 = farm_token.balanceOf(morpheus)

    brownie.chain.mine(1, brownie.chain.time() + week)
    block_timestamp_2 = brownie.chain.time()

    controller.mintFor(reaper_mock, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert farm_token.balanceOf(morpheus) - initial_balance_morpheus_1 == 100 * (block_timestamp_2 - block_timestamp_1)
    initial_balance_morpheus_2 = farm_token.balanceOf(morpheus)

    brownie.chain.mine(1, brownie.chain.time() + 2 * week)
    block_timestamp_3 = brownie.chain.time()

    controller.mintFor(reaper_mock, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert farm_token.balanceOf(morpheus) - initial_balance_morpheus_2 == 100 * (block_timestamp_3 - block_timestamp_2)
    initial_balance_morpheus_3 = farm_token.balanceOf(morpheus)

    brownie.chain.mine(1, brownie.chain.time() + 3 * week)
    block_timestamp_4 = brownie.chain.time()

    controller.mintFor(reaper_mock, morpheus, ZERO_ADDRESS, {'from': morpheus})
    assert farm_token.balanceOf(morpheus) - initial_balance_morpheus_3 == 100 * (block_timestamp_4 - block_timestamp_3)
