import pytest


@pytest.fixture(scope="module")
def MAX_UINT256():
    yield 2 ** 256 - 1
