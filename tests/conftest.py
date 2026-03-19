import os
import pytest
from invoiceninja_mcp.client import InvoiceNinjaClient


def pytest_collection_modifyitems(config, items):
    """Skip tests marked 'writes_data' unless ALLOW_WRITE_TESTS=1 is set."""
    if os.environ.get("ALLOW_WRITE_TESTS") == "1":
        return
    skip_writes = pytest.mark.skip(
        reason="Creates real data. Set ALLOW_WRITE_TESTS=1 to run."
    )
    for item in items:
        if "writes_data" in item.keywords:
            item.add_marker(skip_writes)


@pytest.fixture
def client():
    return InvoiceNinjaClient()
