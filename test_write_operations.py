"""Test write operations - creating draft invoice and expense."""

import asyncio
import sys
from datetime import datetime, timedelta
sys.path.insert(0, 'src')

from invoiceninja_mcp.client import InvoiceNinjaClient
from invoiceninja_mcp.models import Invoice, Expense


async def main():
    """Test creating draft invoice and expense."""
    print("🧪 Testing WRITE Operations (Draft Only)\n")
    print("=" * 60)

    client = InvoiceNinjaClient()

    # First, get a client ID to use for the test invoice
    print("\n🔍 Getting a client ID for test invoice...")
    clients_result = await client.list_clients(per_page=1)
    clients_data = clients_result.get("data", [])

    if not clients_data:
        print("❌ No clients found. Cannot create test invoice.")
        print("   Please create a client in InvoiceNinja first.")
        return

    test_client_id = clients_data[0]["id"]
    test_client_name = clients_data[0].get("name", "Unknown")
    print(f"   Using client: {test_client_name} (ID: {test_client_id})")

    # Test 1: Create a draft invoice
    print("\n1️⃣  Testing: create_invoice() - DRAFT STATUS")
    print("-" * 60)

    today = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    draft_invoice_data = {
        "client_id": test_client_id,  # Required field
        "status_id": 1,  # Draft status
        "number": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "date": today,
        "due_date": due_date,
        "public_notes": "TEST INVOICE - Safe to delete",
        "private_notes": "Created by MCP server test script",
        "line_items": [
            {
                "product_key": "TEST-ITEM",
                "notes": "Test item for MCP server",
                "cost": 10.00,
                "quantity": 1,
                "tax_name1": "VAT",
                "tax_rate1": 21.0
            }
        ]
    }

    try:
        result = await client.create_invoice(draft_invoice_data)
        invoice_data = result.get("data", result)
        invoice = Invoice(**invoice_data)
        print(f"✅ Draft invoice created successfully!")
        print(f"   Invoice #: {invoice.get_invoice_number()}")
        print(f"   ID: {invoice.id}")
        print(f"   Status: {invoice.get_status_name()}")
        print(f"   Amount: ${invoice.amount:.2f}")
        print(f"   ⚠️  Remember to delete this test invoice from InvoiceNinja!")
    except Exception as e:
        print(f"❌ Error creating invoice: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test 2: Create a draft expense
    print("\n2️⃣  Testing: create_expense()")
    print("-" * 60)

    draft_expense_data = {
        "amount": 25.50,
        "expense_date": today,
        "public_notes": "TEST EXPENSE - Safe to delete",
        "private_notes": "Created by MCP server test script",
        "should_be_invoiced": False
    }

    try:
        result = await client.create_expense(draft_expense_data)
        expense_data = result.get("data", result)
        expense = Expense(**expense_data)
        print(f"✅ Expense created successfully!")
        print(f"   ID: {expense.id}")
        print(f"   Amount: ${expense.amount:.2f}")
        print(f"   Date: {expense.expense_date}")
        print(f"   ⚠️  Remember to delete this test expense from InvoiceNinja!")
    except Exception as e:
        print(f"❌ Error creating expense: {str(e)}")
        import traceback
        traceback.print_exc()

    # Test 3: Check if file uploads are supported (just inspect the API)
    print("\n3️⃣  Checking file upload support")
    print("-" * 60)
    print("📝 File uploads for expenses typically use multipart/form-data")
    print("   This would require a separate implementation with file handling")
    print("   Endpoint: POST /api/v1/expenses/{id}/upload")
    print("   Status: Not yet implemented in this MCP server")

    print("\n" + "=" * 60)
    print("✅ Write operation tests completed!")
    print("\n⚠️  IMPORTANT: Please delete the test invoice and expense from")
    print("   your InvoiceNinja instance to keep your data clean.")


if __name__ == "__main__":
    asyncio.run(main())
