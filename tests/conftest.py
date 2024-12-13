import pytest

from manage import read_json_configuration


@pytest.fixture(scope="session")
def app_configuration():
    """Read application configuration for testing."""
    return read_json_configuration("testing")


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", help="run integration tests")


def pytest_runtest_setup(item):
    if "integration" in item.keywords and not item.config.getvalue("integration"):
        pytest.skip("need --integration option to run")
