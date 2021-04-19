import brownie


def test_mint_not_started(controller, reaper_mock, ZERO_ADDRESS, exception_tester, neo):
    controller.addReaper(reaper_mock, {'from': neo})
    exception_tester("minting is not started yet", controller.mintFor,
                     reaper_mock, neo, ZERO_ADDRESS, {'from': neo})
    controller.removeReaper(reaper_mock, {'from': neo})


def test_start_mint_owner_only(controller, ownable_exception_tester, morpheus):
    ownable_exception_tester(controller.startMinting, {'from': morpheus})


def test_start_mint(controller, neo):
    assert not controller.startMintFor()
    controller.startMinting({'from': neo})
    assert controller.startMintFor()


def test_mint(controller, reaper_mock, lp_token, farm_token, ZERO_ADDRESS, neo, morpheus, voting_controller, week):
    controller.addReaper(reaper_mock, {'from': neo})
    controller.startEmission(0, {'from': neo})
    assert controller.startMintFor()

    lp_token.transfer(morpheus, 100, {'from': neo})
    lp_token.approve(reaper_mock, 100, {'from': morpheus})

    brownie.chain.mine(1, brownie.chain.time() + 1)
    tx1 = reaper_mock.deposit(100, {'from': morpheus})
    block_timestamp_1 = tx1.timestamp
    initial_balance_morpheus_1 = farm_token.balanceOf(morpheus)

    brownie.chain.mine(1, block_timestamp_1 + week)

    tx2 = controller.mintFor(reaper_mock, morpheus, ZERO_ADDRESS, {'from': morpheus})
    block_timestamp_2 = tx2.timestamp
    assert farm_token.balanceOf(
        morpheus) - initial_balance_morpheus_1 == 100 * (block_timestamp_2 - block_timestamp_1)
    initial_balance_morpheus_2 = farm_token.balanceOf(morpheus)

    brownie.chain.mine(1, block_timestamp_2 + 2 * week)

    tx3 = controller.mintFor(reaper_mock, morpheus, ZERO_ADDRESS, {'from': morpheus})
    block_timestamp_3 = tx3.timestamp
    assert farm_token.balanceOf(
        morpheus) - initial_balance_morpheus_2 == 100 * (block_timestamp_3 - block_timestamp_2)
    initial_balance_morpheus_3 = farm_token.balanceOf(morpheus)

    brownie.chain.mine(1, block_timestamp_3 + 3 * week)

    tx4 = controller.mintFor(reaper_mock, morpheus, ZERO_ADDRESS, {'from': morpheus})
    block_timestamp_4 = tx4.timestamp
    assert farm_token.balanceOf(
        morpheus) - initial_balance_morpheus_3 == 100 * (block_timestamp_4 - block_timestamp_3)
