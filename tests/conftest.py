import pytest

pytest_plugins = [
    "fixtures.accounts",
]


@pytest.fixture(scope="session")
def ZERO_ADDRESS():
    yield "0x0000000000000000000000000000000000000000"
