"""Quick test script to verify InvoiceNinja connection."""

import asyncio
import sys
sys.path.insert(0, 'src')

from invoiceninja_mcp.client import InvoiceNinjaClient


async def main():
    """Test the connection to InvoiceNinja."""
    client = InvoiceNinjaClient()

    print("🔌 Testing connection to InvoiceNinja API...")
    print(f"   URL: {client.base_url}")
    print()

    try:
        # Try listing clients first (more likely to work than ping)
        print("📋 Testing list_clients...")
        clients = await client.list_clients(per_page=5)
        client_count = len(clients.get("data", []))
        print(f"✅ Connection successful!")
        print(f"   Found {client_count} client(s)")
        print()

        # Try listing invoices
        print("📄 Testing list_invoices...")
        invoices = await client.list_invoices(per_page=5)
        invoice_count = len(invoices.get("data", []))
        print(f"   Found {invoice_count} invoice(s)")
        print()

        # Try listing expenses
        print("💳 Testing list_expenses...")
        expenses = await client.list_expenses(per_page=5)
        expense_count = len(expenses.get("data", []))
        print(f"   Found {expense_count} expense(s)")
        print()

        print("🎉 All tests passed! The MCP server is ready to use.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
