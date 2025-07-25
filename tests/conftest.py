# This file is automatically discovered and imported by pytest when running tests.
# Documentation: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
import logging
import pytest
from newsfeed.utils.logging_config import setup_logging
from newsfeed.ingestion.store import store

# Configure logging for all tests - runs once when this module is imported
setup_logging() 
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def clear_store_before_test():
    """Clears store before every test to keep them isolated"""
    store.clear()
    logger.info("Clear store before tests")
    