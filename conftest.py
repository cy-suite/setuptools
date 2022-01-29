import sys
import os

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--package_name", action="append", default=[],
        help="list of package_name to pass to test functions",
    )
    parser.addoption(
        "--integration", action="store_true", default=False,
        help="run integration tests (only)"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: integration tests")
    if os.environ.get("PRE_BUILT_SETUPTOOLS_WHEEL"):
        config.option.perf_target = os.environ["PRE_BUILT_SETUPTOOLS_WHEEL"]


collect_ignore = [
    'src',
    'tests/manual_test.py',
    'setuptools/_distutils',
    '_distutils_hack',
    'setuptools/extern',
    'pkg_resources/extern',
    'pkg_resources/tests/data',
    'setuptools/_vendor',
    'pkg_resources/_vendor',
]

collect_ignore_glob = [
    '*/mod_with_constant.py',
]


if sys.version_info < (3, 6):
    collect_ignore.append('docs/conf.py')  # uses f-strings
    collect_ignore.append('pavement.py')


@pytest.fixture(autouse=True)
def _skip_integration(request):
    running_integration_tests = request.config.getoption("--integration")
    is_integration_test = request.node.get_closest_marker("integration")
    if running_integration_tests and not is_integration_test:
        pytest.skip("running integration tests only")
    if not running_integration_tests and is_integration_test:
        pytest.skip("skipping integration tests")
