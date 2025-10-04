import pytest
from invoiceninja_mcp.client import InvoiceNinjaClient


@pytest.fixture
def client():
    return InvoiceNinjaClient()
