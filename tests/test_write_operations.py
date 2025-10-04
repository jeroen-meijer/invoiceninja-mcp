import pytest
from datetime import datetime, timedelta
from invoiceninja_mcp.models import Invoice, Expense


@pytest.fixture
async def test_client_id(client):
    clients_result = await client.list_clients(per_page=1)
    clients_data = clients_result.get("data", [])
    if not clients_data:
        pytest.skip("no clients available for testing")
    return clients_data[0]["id"]


@pytest.mark.asyncio
async def test_create_draft_invoice(client, test_client_id):
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    draft_invoice_data = {
        "client_id": test_client_id,
        "status_id": 1,
        "number": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": today,
        "due_date": due_date,
        "public_notes": "TEST INVOICE - Safe to delete",
        "private_notes": "Created by pytest",
        "line_items": [
            {
                "product_key": "TEST-ITEM",
                "notes": "test item",
                "cost": 10.00,
                "quantity": 1,
                "tax_name1": "VAT",
                "tax_rate1": 21.0,
            }
        ],
    }

    result = await client.create_invoice(draft_invoice_data)
    invoice_data = result.get("data", result)
    invoice = Invoice(**invoice_data)

    assert invoice.id is not None
    assert invoice.status_id == 1
    assert invoice.amount > 0


@pytest.mark.asyncio
async def test_create_expense(client):
    today = datetime.now().strftime("%Y-%m-%d")

    draft_expense_data = {
        "amount": 25.50,
        "expense_date": today,
        "public_notes": "TEST EXPENSE - Safe to delete",
        "private_notes": "Created by pytest",
        "should_be_invoiced": False,
    }

    result = await client.create_expense(draft_expense_data)
    expense_data = result.get("data", result)
    expense = Expense(**expense_data)

    assert expense.id is not None
    assert expense.amount == 25.50
