# This file is automatically discovered and imported by pytest when running tests.
# Documentation: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files

from newsfeed.utils.logging_config import setup_logging

# Configure logging for all tests - runs once when this module is imported
setup_logging() 