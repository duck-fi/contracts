import pytest
import brownie


@pytest.fixture(scope="module")
def exception_tester():
    def _test(exception, fn, *args):
        with brownie.reverts(exception):
            fn(*args)

    yield _test
