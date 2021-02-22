import pytest


@pytest.fixture(scope="module")
def day():
    yield 86_400


@pytest.fixture(scope="module")
def week(day):
    yield 7 * day


@pytest.fixture(scope="module")
def year(day):
    yield 365 * day
