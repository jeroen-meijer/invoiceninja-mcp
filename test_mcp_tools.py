"""Test MCP tools to verify functionality."""

import asyncio
import sys
sys.path.insert(0, 'src')

from invoiceninja_mcp.client import InvoiceNinjaClient
from invoiceninja_mcp.models import Invoice, Expense, Client


async def main():
    """Test all MCP tools."""
    print("🧪 Testing MCP Tools via Client\n")
    print("=" * 60)

    client = InvoiceNinjaClient()

    # Test 1: List clients
    print("\n1️⃣  Testing: list_clients()")
    print("-" * 60)
    result = await client.list_clients(per_page=3)
    clients_data = result.get("data", [])
    print(f"Found {len(clients_data)} client(s):")
    for client_data in clients_data:
        c = Client(**client_data)
        print(f"  • {c.name or 'Unnamed'} (ID: {c.id}) - Balance: ${c.balance:.2f}")

    # Test 2: List invoices
    print("\n2️⃣  Testing: list_invoices()")
    print("-" * 60)
    result = await client.list_invoices(per_page=3)
    invoices_data = result.get("data", [])
    print(f"Found {len(invoices_data)} invoice(s):")
    for inv_data in invoices_data:
        inv = Invoice(**inv_data)
        print(f"  • Invoice #{inv.get_invoice_number()} - {inv.get_status_name()} - ${inv.amount:.2f}")

    # Test 3: Get specific invoice
    if invoices_data:
        print("\n3️⃣  Testing: get_invoice()")
        print("-" * 60)
        first_invoice = Invoice(**invoices_data[0])
        result = await client.get_invoice(first_invoice.id)
        inv_detail = Invoice(**result.get("data", result))
        print(f"Invoice #{inv_detail.get_invoice_number()}")
        print(f"  Total (incl. tax): ${inv_detail.get_amount_incl_tax():.2f}")
        print(f"  Total (excl. tax): ${inv_detail.get_amount_excl_tax():.2f}")
        print(f"  Tax: ${inv_detail.total_taxes or 0:.2f}")

    # Test 4: List expenses
    print("\n4️⃣  Testing: list_expenses()")
    print("-" * 60)
    result = await client.list_expenses(per_page=3)
    expenses_data = result.get("data", [])
    print(f"Found {len(expenses_data)} expense(s):")
    for exp_data in expenses_data:
        exp = Expense(**exp_data)
        print(f"  • Expense ${exp.amount:.2f} - {exp.expense_date or 'No date'}")

    # Test 5: List vendors
    print("\n5️⃣  Testing: list_vendors()")
    print("-" * 60)
    result = await client.list_vendors(per_page=3)
    vendors = result.get("data", [])
    print(f"Found {len(vendors)} vendor(s)")

    # Test 6: List expense categories
    print("\n6️⃣  Testing: list_expense_categories()")
    print("-" * 60)
    result = await client.list_expense_categories(per_page=3)
    categories = result.get("data", [])
    print(f"Found {len(categories)} expense category(ies)")

    print("\n" + "=" * 60)
    print("✅ All MCP tools tested successfully!")


if __name__ == "__main__":
    asyncio.run(main())
