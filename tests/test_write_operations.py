import pytest
from datetime import datetime, timedelta
from invoiceninja_mcp.models import Invoice, Expense, Vendor


async def get_test_client_id(client):
    clients_result = await client.list_clients(per_page=1)
    clients_data = clients_result.get("data", [])
    if not clients_data:
        pytest.skip("no clients available for testing")
    return clients_data[0]["id"]


@pytest.mark.asyncio
async def test_create_draft_invoice(client):
    test_client_id = await get_test_client_id(client)
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


@pytest.mark.asyncio
async def test_create_expense_with_tax(client):
    today = datetime.now().strftime("%Y-%m-%d")

    expense_data = {
        "amount": 2700.00,
        "expense_date": today,
        "public_notes": "TEST EXPENSE WITH TAX - Safe to delete",
        "private_notes": "Created by pytest",
        "tax_rate1": 21.0,
        "tax_name1": "BTW (Reverse Charged)",
        "should_be_invoiced": False,
    }

    result = await client.create_expense(expense_data)
    expense = Expense(**result.get("data", result))

    assert expense.id is not None
    assert expense.amount == 2700.00
    assert expense.tax_rate1 == 21.0
    assert expense.tax_name1 == "BTW (Reverse Charged)"


@pytest.mark.asyncio
async def test_update_expense(client):
    today = datetime.now().strftime("%Y-%m-%d")

    draft_expense_data = {
        "amount": 100.00,
        "expense_date": today,
        "public_notes": "TEST EXPENSE - Before update",
        "private_notes": "Created by pytest",
        "should_be_invoiced": False,
    }

    create_result = await client.create_expense(draft_expense_data)
    expense = Expense(**create_result.get("data", create_result))

    update_data = {
        "amount": 150.75,
        "public_notes": "TEST EXPENSE - After update",
        "private_notes": "Updated by pytest",
    }

    update_result = await client.update_expense(expense.id, update_data)
    updated_expense = Expense(**update_result.get("data", update_result))

    assert updated_expense.id == expense.id
    assert updated_expense.amount == 150.75
    assert updated_expense.public_notes == "TEST EXPENSE - After update"


@pytest.mark.asyncio
async def test_list_expenses_with_date_range(client):
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    result = await client.list_expenses(
        per_page=10, start_date=start_date, end_date=end_date
    )
    expenses_data = result.get("data", [])

    assert isinstance(expenses_data, list)
    for expense_data in expenses_data:
        expense = Expense(**expense_data)
        if expense.expense_date:
            assert start_date <= expense.expense_date <= end_date


@pytest.mark.asyncio
async def test_create_vendor(client):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    vendor_data = {
        "name": f"TEST-VENDOR-{timestamp}",
        "phone": "555-1234",
        "website": "https://test.example.com",
    }

    result = await client.create_vendor(vendor_data)
    vendor_result = result.get("data", result)
    vendor = Vendor(**vendor_result)

    assert vendor.id is not None
    assert vendor.name.startswith("TEST-VENDOR-")
    assert vendor.phone == "555-1234"


@pytest.mark.asyncio
async def test_clone_invoice(client):
    test_client_id = await get_test_client_id(client)
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    original_invoice_data = {
        "client_id": test_client_id,
        "status_id": 1,
        "number": f"ORIG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": today,
        "due_date": due_date,
        "public_notes": "TEST INVOICE TO CLONE - Safe to delete",
        "line_items": [
            {
                "product_key": "TEST-ITEM",
                "notes": "original item",
                "cost": 100.00,
                "quantity": 1,
            }
        ],
    }

    create_result = await client.create_invoice(original_invoice_data)
    original_invoice = Invoice(**create_result.get("data", create_result))

    clone_result = await client.clone_invoice(original_invoice.id)
    clone_data = clone_result.get("data", clone_result)

    assert isinstance(clone_data, list)
    assert len(clone_data) > 0

    cloned_invoice = Invoice(**clone_data[0])
    assert cloned_invoice.id is not None
    assert cloned_invoice.status_id == 1
    assert cloned_invoice.client_id == original_invoice.client_id


@pytest.mark.asyncio
async def test_update_invoice(client):
    test_client_id = await get_test_client_id(client)
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    draft_invoice_data = {
        "client_id": test_client_id,
        "status_id": 1,
        "number": f"UPDATE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": today,
        "due_date": due_date,
        "public_notes": "TEST INVOICE - Before update",
        "line_items": [
            {"product_key": "TEST-ITEM", "notes": "original", "cost": 50.00, "quantity": 1}
        ],
    }

    create_result = await client.create_invoice(draft_invoice_data)
    invoice = Invoice(**create_result.get("data", create_result))

    new_due_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
    update_data = {
        "public_notes": "TEST INVOICE - After update",
        "due_date": new_due_date,
        "line_items": [
            {
                "product_key": "TEST-ITEM-UPDATED",
                "notes": "updated item",
                "cost": 75.00,
                "quantity": 2,
            }
        ],
    }

    update_result = await client.update_invoice(invoice.id, update_data)
    updated_invoice = Invoice(**update_result.get("data", update_result))

    assert updated_invoice.id == invoice.id
    assert updated_invoice.public_notes == "TEST INVOICE - After update"
    assert updated_invoice.due_date == new_due_date


@pytest.mark.asyncio
async def test_get_latest_invoice_for_client(client):
    test_client_id = await get_test_client_id(client)

    result = await client.list_invoices(client_id=test_client_id, per_page=1, sort="date|desc")
    invoices = result.get("data", [])

    if not invoices:
        pytest.skip("no invoices available for test client")

    latest_invoice = Invoice(**invoices[0])
    assert latest_invoice.id is not None
    assert latest_invoice.client_id == test_client_id


@pytest.mark.asyncio
async def test_invoice_with_task_line_items(client):
    test_client_id = await get_test_client_id(client)
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    invoice_with_tasks_data = {
        "client_id": test_client_id,
        "status_id": 1,
        "number": f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": today,
        "due_date": due_date,
        "public_notes": "TEST INVOICE WITH TASK ITEMS - Safe to delete",
        "line_items": [
            {
                "type_id": "2",
                "product_key": "Development",
                "notes": "Frontend development work",
                "cost": 100.00,
                "quantity": 8,
                "date": today,
            },
            {
                "type_id": "1",
                "product_key": "HOSTING",
                "notes": "Monthly hosting",
                "cost": 50.00,
                "quantity": 1,
            },
        ],
    }

    create_result = await client.create_invoice(invoice_with_tasks_data)
    invoice = Invoice(**create_result.get("data", create_result))

    assert invoice.id is not None
    assert len(invoice.line_items) == 2

    task_item = invoice.line_items[0]
    assert task_item.type_id is not None
    assert task_item.product_key == "Development"

    clone_result = await client.clone_invoice(invoice.id)
    clone_data = clone_result.get("data", clone_result)
    cloned_invoice = Invoice(**clone_data[0])

    assert cloned_invoice.id is not None
    assert len(cloned_invoice.line_items) >= 1


@pytest.mark.asyncio
async def test_invoice_workflow_clone_update_review(client):
    test_client_id = await get_test_client_id(client)
    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    original_invoice_data = {
        "client_id": test_client_id,
        "status_id": 1,
        "number": f"MONTHLY-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": today,
        "due_date": due_date,
        "public_notes": "Monthly invoice - October 2024",
        "line_items": [
            {
                "product_key": "CONSULTING",
                "notes": "Consulting services - October 2024",
                "cost": 1000.00,
                "quantity": 1,
            }
        ],
    }

    create_result = await client.create_invoice(original_invoice_data)
    october_invoice = Invoice(**create_result.get("data", create_result))

    clone_result = await client.clone_invoice(october_invoice.id)
    clone_data = clone_result.get("data", clone_result)
    november_draft = Invoice(**clone_data[0])

    next_month_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    next_month_due = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")

    update_data = {
        "date": next_month_date,
        "due_date": next_month_due,
        "public_notes": "Monthly invoice - November 2024",
        "line_items": [
            {
                "product_key": "CONSULTING",
                "notes": "Consulting services - November 2024",
                "cost": 1200.00,
                "quantity": 1,
            }
        ],
    }

    update_result = await client.update_invoice(november_draft.id, update_data)
    updated_invoice = Invoice(**update_result.get("data", update_result))

    assert updated_invoice.id is not None
    assert updated_invoice.status_id == 1
    assert updated_invoice.public_notes == "Monthly invoice - November 2024"
    assert updated_invoice.date == next_month_date
