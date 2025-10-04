import pytest
from invoiceninja_mcp.models import Invoice, Expense, Client


@pytest.mark.asyncio
async def test_list_clients(client):
    result = await client.list_clients(per_page=3)
    clients_data = result.get("data", [])
    assert isinstance(clients_data, list)
    if clients_data:
        c = Client(**clients_data[0])
        assert c.id is not None


@pytest.mark.asyncio
async def test_list_invoices(client):
    result = await client.list_invoices(per_page=3)
    invoices_data = result.get("data", [])
    assert isinstance(invoices_data, list)
    if invoices_data:
        inv = Invoice(**invoices_data[0])
        assert inv.id is not None
        assert inv.get_invoice_number() is not None


@pytest.mark.asyncio
async def test_get_invoice(client):
    result = await client.list_invoices(per_page=1)
    invoices_data = result.get("data", [])
    if invoices_data:
        first_invoice = Invoice(**invoices_data[0])
        detail_result = await client.get_invoice(first_invoice.id)
        inv_detail = Invoice(**detail_result.get("data", detail_result))
        assert inv_detail.id == first_invoice.id
        assert inv_detail.get_amount_incl_tax() >= 0


@pytest.mark.asyncio
async def test_list_expenses(client):
    result = await client.list_expenses(per_page=3)
    expenses_data = result.get("data", [])
    assert isinstance(expenses_data, list)
    if expenses_data:
        exp = Expense(**expenses_data[0])
        assert exp.id is not None
        assert exp.amount >= 0


@pytest.mark.asyncio
async def test_list_vendors(client):
    result = await client.list_vendors(per_page=3)
    vendors = result.get("data", [])
    assert isinstance(vendors, list)


@pytest.mark.asyncio
async def test_list_expense_categories(client):
    result = await client.list_expense_categories(per_page=3)
    categories = result.get("data", [])
    assert isinstance(categories, list)
