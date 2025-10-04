import pytest
from datetime import datetime
from invoiceninja_mcp.models import Invoice, Expense, Client, Vendor


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


@pytest.mark.asyncio
async def test_mcp_create_expense(client):
    today = datetime.now().strftime("%Y-%m-%d")
    expense_data = {
        "amount": 50.25,
        "expense_date": today,
        "public_notes": "TEST MCP EXPENSE",
    }
    result = await client.create_expense(expense_data)
    expense = result.get("data", result)
    assert expense["amount"] == 50.25


@pytest.mark.asyncio
async def test_mcp_create_vendor(client):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    vendor_data = {"name": f"TEST-MCP-VENDOR-{timestamp}", "phone": "555-9999"}
    result = await client.create_vendor(vendor_data)
    vendor = result.get("data", result)
    assert f"TEST-MCP-VENDOR-{timestamp}" in vendor["name"]


@pytest.mark.asyncio
async def test_search_vendors(client):
    await client.create_vendor({"name": "Versio Hosting BV"})
    await client.create_vendor({"name": "Google Cloud"})

    result = await client.list_vendors(per_page=500)
    vendors = result.get("data", [])

    versio_matches = [v for v in vendors if "versio" in v["name"].lower()]
    assert len(versio_matches) > 0


@pytest.mark.asyncio
async def test_btw_quarterly_report(client):
    current_year = datetime.now().year
    start_date, end_date = (f"{current_year}-01-01", f"{current_year}-03-31")

    invoices_result = await client.list_invoices(per_page=500)
    expenses_result = await client.list_expenses(per_page=500)

    invoices = invoices_result.get("data", [])
    expenses = expenses_result.get("data", [])

    total_btw_invoices = 0.0
    total_btw_expenses = 0.0

    for invoice in invoices:
        if invoice.get("date") and start_date <= invoice["date"] <= end_date:
            total_btw_invoices += invoice.get("total_taxes", 0) or 0

    for expense in expenses:
        expense_date = expense.get("expense_date") or expense.get("date")
        if expense_date and start_date <= expense_date <= end_date:
            tax_rate1 = expense.get("tax_rate1", 0) or 0
            if tax_rate1 == 21:
                expense_amount = expense.get("amount", 0) or 0
                total_btw_expenses += expense_amount * 0.21

    assert total_btw_invoices >= 0
    assert total_btw_expenses >= 0
