import pytest
import brownie


@pytest.fixture
def exception_tester():
    def _test(exception, fn, *args):
        with brownie.reverts(exception):
            fn(*args)

    yield _test
