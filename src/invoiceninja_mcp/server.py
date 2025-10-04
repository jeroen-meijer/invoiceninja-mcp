"""InvoiceNinja MCP Server with FastMCP."""

from fastmcp import FastMCP
from datetime import datetime, date
from typing import Optional
import json

from .client import InvoiceNinjaClient
from .models import Invoice, Expense, Client, Vendor, ExpenseCategory, INVOICE_STATUS

# Initialize FastMCP server
mcp = FastMCP("InvoiceNinja MCP Server")

# Initialize InvoiceNinja client
client = InvoiceNinjaClient()


# Utility function for quarterly date calculations
def get_quarter_dates(year: int, quarter: int) -> tuple[str, str]:
    """Get start and end dates for a quarter."""
    quarters = {
        1: (f"{year}-01-01", f"{year}-03-31"),
        2: (f"{year}-04-01", f"{year}-06-30"),
        3: (f"{year}-07-01", f"{year}-09-30"),
        4: (f"{year}-10-01", f"{year}-12-31")
    }
    return quarters.get(quarter, (f"{year}-01-01", f"{year}-12-31"))


# ==================== UTILITY TOOLS ====================

@mcp.tool()
async def test_connection() -> str:
    """Test the connection to InvoiceNinja API."""
    try:
        result = await client.test_connection()
        return f"✅ Successfully connected to InvoiceNinja API!\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Connection failed: {str(e)}"


@mcp.tool()
async def list_clients(per_page: int = 100) -> str:
    """
    List all clients from InvoiceNinja.

    Args:
        per_page: Number of clients to return (default: 100)
    """
    try:
        result = await client.list_clients(per_page=per_page)
        clients_data = result.get("data", [])

        if not clients_data:
            return "No clients found."

        output = [f"Found {len(clients_data)} client(s):\n"]
        for client_data in clients_data:
            c = Client(**client_data)
            output.append(f"• {c.name or 'Unnamed'} (ID: {c.id})")
            if c.balance:
                output.append(f"  Balance: ${c.balance:.2f}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing clients: {str(e)}"


@mcp.tool()
async def list_vendors(per_page: int = 100) -> str:
    """
    List all vendors from InvoiceNinja.

    Args:
        per_page: Number of vendors to return (default: 100)
    """
    try:
        result = await client.list_vendors(per_page=per_page)
        vendors_data = result.get("data", [])

        if not vendors_data:
            return "No vendors found."

        output = [f"Found {len(vendors_data)} vendor(s):\n"]
        for vendor_data in vendors_data:
            v = Vendor(**vendor_data)
            output.append(f"• {v.name or 'Unnamed'} (ID: {v.id})")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing vendors: {str(e)}"


@mcp.tool()
async def list_expense_categories(per_page: int = 100) -> str:
    """
    List all expense categories from InvoiceNinja.

    Args:
        per_page: Number of categories to return (default: 100)
    """
    try:
        result = await client.list_expense_categories(per_page=per_page)
        categories_data = result.get("data", [])

        if not categories_data:
            return "No expense categories found."

        output = [f"Found {len(categories_data)} expense category(ies):\n"]
        for cat_data in categories_data:
            cat = ExpenseCategory(**cat_data)
            output.append(f"• {cat.name} (ID: {cat.id})")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing expense categories: {str(e)}"


# ==================== INVOICE TOOLS ====================

@mcp.tool()
async def list_invoices(
    status: Optional[str] = None,
    client_id: Optional[str] = None,
    per_page: int = 20
) -> str:
    """
    List invoices with optional filters.

    Args:
        status: Filter by status (draft, sent, viewed, approved, partial, paid)
        client_id: Filter by client ID
        per_page: Number of invoices to return (default: 20)
    """
    try:
        result = await client.list_invoices(
            status=status,
            client_id=client_id,
            per_page=per_page
        )
        invoices_data = result.get("data", [])

        if not invoices_data:
            return "No invoices found."

        output = [f"Found {len(invoices_data)} invoice(s):\n"]
        for inv_data in invoices_data:
            inv = Invoice(**inv_data)
            output.append(f"\n📄 Invoice #{inv.get_invoice_number()}")
            output.append(f"   Status: {inv.get_status_name()}")
            output.append(f"   Total (incl. tax): ${inv.get_amount_incl_tax():.2f}")
            output.append(f"   Total (excl. tax): ${inv.get_amount_excl_tax():.2f}")
            output.append(f"   Balance: ${inv.balance:.2f}")
            if inv.date:
                output.append(f"   Date: {inv.date}")
            if inv.due_date:
                output.append(f"   Due Date: {inv.due_date}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing invoices: {str(e)}"


@mcp.tool()
async def get_invoice(invoice_id: str) -> str:
    """
    Get detailed information about a specific invoice.

    Args:
        invoice_id: The ID of the invoice
    """
    try:
        result = await client.get_invoice(invoice_id)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data)

        output = [f"📄 Invoice #{inv.get_invoice_number()}\n"]
        output.append(f"ID: {inv.id}")
        output.append(f"Status: {inv.get_status_name()}")
        output.append(f"\n💰 Amounts:")
        output.append(f"   Total (incl. tax): ${inv.get_amount_incl_tax():.2f}")
        output.append(f"   Total (excl. tax): ${inv.get_amount_excl_tax():.2f}")
        output.append(f"   Tax Amount: ${inv.total_taxes or 0:.2f}")
        output.append(f"   Balance Due: ${inv.balance:.2f}")

        if inv.date:
            output.append(f"\n📅 Dates:")
            output.append(f"   Invoice Date: {inv.date}")
        if inv.due_date:
            output.append(f"   Due Date: {inv.due_date}")
        if inv.last_sent_date:
            output.append(f"   Last Sent: {inv.last_sent_date}")

        if inv.public_notes:
            output.append(f"\n📝 Notes: {inv.public_notes}")

        if inv.line_items:
            output.append(f"\n📋 Line Items ({len(inv.line_items)}):")
            for idx, item in enumerate(inv.line_items, 1):
                output.append(f"   {idx}. {item.product_key or 'Item'}")
                if item.notes:
                    output.append(f"      {item.notes}")
                if item.quantity and item.cost:
                    output.append(f"      Qty: {item.quantity} × ${item.cost:.2f} = ${item.line_total or 0:.2f}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error getting invoice: {str(e)}"


@mcp.tool()
async def get_invoice_status(invoice_id: str) -> str:
    """
    Get the current status of an invoice.

    Args:
        invoice_id: The ID of the invoice
    """
    try:
        result = await client.get_invoice(invoice_id)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data)

        return f"Invoice #{inv.get_invoice_number()}: {inv.get_status_name()}"
    except Exception as e:
        return f"❌ Error getting invoice status: {str(e)}"


# ==================== EXPENSE TOOLS ====================

@mcp.tool()
async def list_expenses(per_page: int = 20) -> str:
    """
    List expenses from InvoiceNinja.

    Args:
        per_page: Number of expenses to return (default: 20)
    """
    try:
        result = await client.list_expenses(per_page=per_page)
        expenses_data = result.get("data", [])

        if not expenses_data:
            return "No expenses found."

        output = [f"Found {len(expenses_data)} expense(s):\n"]
        for exp_data in expenses_data:
            exp = Expense(**exp_data)
            output.append(f"\n💳 Expense (ID: {exp.id})")
            output.append(f"   Amount: ${exp.amount:.2f}")
            if exp.expense_date:
                output.append(f"   Date: {exp.expense_date}")
            if exp.public_notes:
                output.append(f"   Notes: {exp.public_notes}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing expenses: {str(e)}"


@mcp.tool()
async def get_expense(expense_id: str) -> str:
    """
    Get detailed information about a specific expense.

    Args:
        expense_id: The ID of the expense
    """
    try:
        result = await client.get_expense(expense_id)
        exp_data = result.get("data", result)
        exp = Expense(**exp_data)

        output = [f"💳 Expense Details\n"]
        output.append(f"ID: {exp.id}")
        output.append(f"Amount: ${exp.amount:.2f}")

        if exp.expense_date:
            output.append(f"Date: {exp.expense_date}")
        if exp.payment_date:
            output.append(f"Payment Date: {exp.payment_date}")

        if exp.category_id:
            output.append(f"Category ID: {exp.category_id}")
        if exp.vendor_id:
            output.append(f"Vendor ID: {exp.vendor_id}")
        if exp.client_id:
            output.append(f"Client ID: {exp.client_id}")

        if exp.public_notes:
            output.append(f"\n📝 Public Notes: {exp.public_notes}")
        if exp.private_notes:
            output.append(f"🔒 Private Notes: {exp.private_notes}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error getting expense: {str(e)}"


# ==================== REPORT TOOLS ====================

@mcp.tool()
async def get_tax_report_quarterly(year: int, quarter: int) -> str:
    """
    Get tax report for a specific quarter.

    Args:
        year: The year (e.g., 2024)
        quarter: The quarter (1, 2, 3, or 4)
    """
    try:
        if quarter not in [1, 2, 3, 4]:
            return "❌ Quarter must be 1, 2, 3, or 4"

        start_date, end_date = get_quarter_dates(year, quarter)

        result = await client.get_reports(
            report_type="tax_summary",
            start_date=start_date,
            end_date=end_date
        )

        return f"📊 Tax Report for Q{quarter} {year} ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting tax report: {str(e)}"


@mcp.tool()
async def get_tax_report_custom(start_date: str, end_date: str) -> str:
    """
    Get tax report for a custom date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        result = await client.get_reports(
            report_type="tax_summary",
            start_date=start_date,
            end_date=end_date
        )

        return f"📊 Tax Report ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting tax report: {str(e)}"


@mcp.tool()
async def get_expense_report(start_date: str, end_date: str) -> str:
    """
    Get expense report for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        result = await client.get_reports(
            report_type="expense_summary",
            start_date=start_date,
            end_date=end_date
        )

        return f"📊 Expense Report ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting expense report: {str(e)}"


@mcp.tool()
async def get_invoice_report(start_date: str, end_date: str) -> str:
    """
    Get invoice report for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    try:
        result = await client.get_reports(
            report_type="invoice_summary",
            start_date=start_date,
            end_date=end_date
        )

        return f"📊 Invoice Report ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting invoice report: {str(e)}"


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
