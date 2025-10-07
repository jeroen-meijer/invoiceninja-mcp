from fastmcp import FastMCP
import json
import subprocess
import tempfile
import os
from pathlib import Path

from .client import InvoiceNinjaClient
from .models import Invoice, Expense, Client, Vendor, ExpenseCategory

mcp = FastMCP("InvoiceNinja MCP Server")
client = InvoiceNinjaClient()


def get_quarter_dates(year: int, quarter: int) -> tuple[str, str]:
    quarters = {
        1: (f"{year}-01-01", f"{year}-03-31"),
        2: (f"{year}-04-01", f"{year}-06-30"),
        3: (f"{year}-07-01", f"{year}-09-30"),
        4: (f"{year}-10-01", f"{year}-12-31"),
    }
    return quarters.get(quarter, (f"{year}-01-01", f"{year}-12-31"))


@mcp.tool()
async def test_connection() -> str:
    try:
        result = await client.test_connection()
        return f"✅ Successfully connected to InvoiceNinja API!\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Connection failed: {str(e)}"


@mcp.tool()
async def list_clients(per_page: int = 100) -> str:
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
async def search_vendors(search_term: str) -> str:
    try:
        result = await client.list_vendors(per_page=500)
        vendors_data = result.get("data", [])

        if not vendors_data:
            return "No vendors found."

        search_lower = search_term.lower()
        matches = []

        for vendor_data in vendors_data:
            v = Vendor(**vendor_data)
            vendor_name = (v.name or "").lower()

            if search_lower in vendor_name or vendor_name in search_lower:
                score = len(set(search_lower.split()) & set(vendor_name.split()))
                matches.append((score, v))

        matches.sort(key=lambda x: x[0], reverse=True)

        if not matches:
            return f"No vendors found matching '{search_term}'"

        output = [f"Found {len(matches)} vendor(s) matching '{search_term}':\n"]
        for score, v in matches[:10]:
            output.append(f"• {v.name or 'Unnamed'} (ID: {v.id})")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error searching vendors: {str(e)}"


@mcp.tool()
async def list_expense_categories(per_page: int = 100) -> str:
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


@mcp.tool()
async def list_invoices(
    status: str | None = "Active", client_id: str | None = None, per_page: int = 20
) -> str:
    try:
        result = await client.list_invoices(
            status=status, client_id=client_id, per_page=per_page
        )
        invoices_data = result.get("data", [])

        if not invoices_data:
            return "No invoices found."

        output = [f"Found {len(invoices_data)} invoice(s):\n"]
        for inv_data in invoices_data:
            inv = Invoice(**inv_data)
            output.append(f"\n📄 Invoice #{inv.get_invoice_number()} (ID: {inv.id})")
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
    try:
        result = await client.get_invoice(invoice_id)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data)

        output = [f"📄 Invoice #{inv.get_invoice_number()}\n"]
        output.append(f"ID: {inv.id}")
        output.append(f"Status: {inv.get_status_name()}")
        output.append("\n💰 Amounts:")
        output.append(f"   Total (incl. tax): ${inv.get_amount_incl_tax():.2f}")
        output.append(f"   Total (excl. tax): ${inv.get_amount_excl_tax():.2f}")
        output.append(f"   Tax Amount: ${inv.total_taxes or 0:.2f}")
        output.append(f"   Balance Due: ${inv.balance:.2f}")

        if inv.date:
            output.append("\n📅 Dates:")
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
                    output.append(
                        f"      Qty: {item.quantity} × ${item.cost:.2f} = ${item.line_total or 0:.2f}"
                    )

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error getting invoice: {str(e)}"


@mcp.tool()
async def get_invoice_status(invoice_id: str) -> str:
    try:
        result = await client.get_invoice(invoice_id)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data)

        return f"Invoice #{inv.get_invoice_number()}: {inv.get_status_name()}"
    except Exception as e:
        return f"❌ Error getting invoice status: {str(e)}"


@mcp.tool()
async def get_latest_invoice_for_client(client_id: str) -> str:
    try:
        result = await client.list_invoices(
            client_id=client_id, per_page=1, sort="date|desc"
        )
        invoices_data = result.get("data", [])

        if not invoices_data:
            return f"No invoices found for client ID: {client_id}"

        inv = Invoice(**invoices_data[0])

        output = [f"📄 Latest Invoice for Client {client_id}\n"]
        output.append(f"Invoice #{inv.get_invoice_number()} (ID: {inv.id})")
        output.append(f"Status: {inv.get_status_name()}")
        output.append(f"Total (incl. tax): ${inv.get_amount_incl_tax():.2f}")
        output.append(f"Balance: ${inv.balance:.2f}")
        if inv.date:
            output.append(f"Date: {inv.date}")
        if inv.due_date:
            output.append(f"Due Date: {inv.due_date}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error getting latest invoice: {str(e)}"


@mcp.tool()
async def clone_invoice(invoice_id: str) -> str:
    try:
        result = await client.clone_invoice(invoice_id)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data[0])

        output = [f"✅ Invoice cloned successfully!\n"]
        output.append(f"New Invoice ID: {inv.id}")
        output.append(f"Invoice Number: {inv.get_invoice_number()}")
        output.append(f"Status: {inv.get_status_name()}")
        output.append(f"Total: ${inv.get_amount_incl_tax():.2f}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error cloning invoice: {str(e)}"


@mcp.tool()
async def update_invoice(invoice_id: str, invoice_data: str) -> str:
    try:
        import json

        data = json.loads(invoice_data)
        result = await client.update_invoice(invoice_id, data)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data)

        output = [f"✅ Invoice updated successfully!\n"]
        output.append(f"Invoice #{inv.get_invoice_number()} (ID: {inv.id})")
        output.append(f"Status: {inv.get_status_name()}")
        output.append(f"Total (incl. tax): ${inv.get_amount_incl_tax():.2f}")
        if inv.date:
            output.append(f"Date: {inv.date}")
        if inv.due_date:
            output.append(f"Due Date: {inv.due_date}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error updating invoice: {str(e)}"


@mcp.tool()
async def email_invoice(invoice_id: str) -> str:
    try:
        result = await client.bulk_invoices("email", [invoice_id])

        return f"✅ Invoice {invoice_id} has been emailed successfully!\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error emailing invoice: {str(e)}"


@mcp.tool()
async def mark_invoice_sent(invoice_id: str) -> str:
    try:
        result = await client.bulk_invoices("mark_sent", [invoice_id])

        return f"✅ Invoice {invoice_id} marked as sent!\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error marking invoice as sent: {str(e)}"


@mcp.tool()
async def mark_invoice_paid(invoice_id: str) -> str:
    try:
        result = await client.bulk_invoices("mark_paid", [invoice_id])

        return f"✅ Invoice {invoice_id} marked as paid!\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error marking invoice as paid: {str(e)}"


@mcp.tool()
async def preview_invoice_pdf(invoice_id: str) -> str:
    try:
        inv_result = await client.get_invoice(invoice_id)
        inv_data = inv_result.get("data", inv_result)
        inv = Invoice(**inv_data)

        pdf_content = await client.download_invoice_pdf(invoice_id)

        invoice_number = inv.get_invoice_number()
        filename = f"invoice_{invoice_number}.pdf"
        temp_dir = Path(tempfile.gettempdir())
        pdf_path = temp_dir / filename

        with open(pdf_path, "wb") as f:
            f.write(pdf_content)

        if os.name == "posix":
            if os.uname().sysname == "Darwin":
                subprocess.run(["open", str(pdf_path)])
            else:
                subprocess.run(["xdg-open", str(pdf_path)])
        elif os.name == "nt":
            os.startfile(str(pdf_path))

        return f"✅ Invoice PDF downloaded and opened!\nFile saved to: {pdf_path}"
    except Exception as e:
        return f"❌ Error previewing invoice PDF: {str(e)}"


@mcp.tool()
async def get_invoice_preview_url(invoice_id: str) -> str:
    try:
        inv_result = await client.get_invoice(invoice_id)
        inv_data = inv_result.get("data", inv_result)
        inv = Invoice(**inv_data)

        if inv.invitations and len(inv.invitations) > 0:
            invitation_key = inv.invitations[0].get("key")
            if invitation_key:
                base_url = client.base_url.replace("/api/v1", "")
                preview_url = f"{base_url}/client/invoice/{invitation_key}"

                return f"📄 Invoice #{inv.get_invoice_number()}\n\n🔗 Preview URL:\n{preview_url}\n\nOpen this URL in your browser to view the invoice PDF."
            else:
                return f"❌ No invitation key found for invoice {invoice_id}"
        else:
            return f"❌ No invitations found for invoice {invoice_id}"
    except Exception as e:
        return f"❌ Error getting invoice preview URL: {str(e)}"


@mcp.tool()
async def list_expenses(
    per_page: int = 20,
    start_date: str | None = None,
    end_date: str | None = None,
    vendor_id: str | None = None,
) -> str:
    try:
        result = await client.list_expenses(
            per_page=per_page,
            start_date=start_date,
            end_date=end_date,
            vendor_id=vendor_id,
        )
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
            if exp.vendor_id:
                output.append(f"   Vendor ID: {exp.vendor_id}")
            if exp.public_notes:
                output.append(f"   Notes: {exp.public_notes}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error listing expenses: {str(e)}"


@mcp.tool()
async def get_expense(expense_id: str) -> str:
    try:
        result = await client.get_expense(expense_id)
        exp_data = result.get("data", result)
        exp = Expense(**exp_data)

        output = ["💳 Expense Details\n"]
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


@mcp.tool()
async def get_tax_report_quarterly(year: int, quarter: int) -> str:
    try:
        if quarter not in [1, 2, 3, 4]:
            return "❌ Quarter must be 1, 2, 3, or 4"

        start_date, end_date = get_quarter_dates(year, quarter)

        result = await client.get_reports(
            report_type="tax_summary", start_date=start_date, end_date=end_date
        )

        return f"📊 Tax Report for Q{quarter} {year} ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting tax report: {str(e)}"


async def _generate_btw_report(
    year: int, quarter: int, api_client: InvoiceNinjaClient
) -> str:
    if quarter not in [1, 2, 3, 4]:
        return "❌ Quarter must be 1, 2, 3, or 4"

    start_date, end_date = get_quarter_dates(year, quarter)

    report = {
        "year": year,
        "quarter": quarter,
        "total_billed": 0.0,
        "total_billed_ex_btw": 0.0,
        "total_btw_invoices": 0.0,
        "total_expenses": 0.0,
        "total_btw_expenses": 0.0,
        "total_difference": 0.0,
    }

    invoices_result = await api_client.list_invoices(
        per_page=500,
        sort="date|desc",
        include="client",
        without_deleted_clients=True,
    )
    invoices = invoices_result.get("data", [])

    for invoice in invoices:
        if invoice.get("date"):
            invoice_date = invoice["date"]
            if start_date <= invoice_date <= end_date:
                btw = invoice.get("total_taxes", 0) or 0
                amount = invoice.get("amount", 0) or 0
                ex_btw = amount - btw

                report["total_billed"] += amount
                report["total_billed_ex_btw"] += ex_btw
                report["total_btw_invoices"] += btw

    expenses_result = await api_client.list_expenses(
        per_page=500, sort="expense_date|desc", include="client,vendor,category"
    )
    expenses = expenses_result.get("data", [])

    for expense in expenses:
        expense_date = expense.get("expense_date") or expense.get("date")
        if expense_date and start_date <= expense_date <= end_date:
            expense_amount = expense.get("amount", 0) or 0
            tax_rate1 = expense.get("tax_rate1", 0) or 0

            expense_btw = 0
            if tax_rate1 == 21:
                expense_btw = expense_amount * 0.21
                report["total_btw_expenses"] += expense_btw

            report["total_expenses"] += expense_amount

    report["total_difference"] = (
        report["total_btw_invoices"] - report["total_btw_expenses"]
    )

    table_data = [
        ["Quarter", f"{year}-Q{quarter}"],
        ["Total amount billed", f"€{report['total_billed']:.2f}"],
        ["Exact amount billed ex BTW", f"€{report['total_billed_ex_btw']:.2f}"],
        [
            "Total BTW amount over invoices",
            f"€{report['total_btw_invoices']:.2f}",
        ],
        ["Total expenses", f"€{report['total_expenses']:.2f}"],
        ["BTW paid over these expenses", f"€{report['total_btw_expenses']:.2f}"],
        ["Total BTW difference", f"€{report['total_difference']:.2f}"],
    ]

    output = [f"📊 BTW Quarterly Report for Q{quarter} {year}\n"]
    output.append(f"Period: {start_date} to {end_date}\n")
    output.append("| Description | Amount |")
    output.append("|-------------|--------|")
    for row in table_data:
        output.append(f"| {row[0]} | {row[1]} |")

    return "\n".join(output)


@mcp.tool()
async def get_btw_quarterly_report(year: int, quarter: int) -> str:
    try:
        return await _generate_btw_report(year, quarter, client)
    except Exception as e:
        return f"❌ Error generating BTW report: {str(e)}"


@mcp.tool()
async def get_tax_report_custom(start_date: str, end_date: str) -> str:
    try:
        result = await client.get_reports(
            report_type="tax_summary", start_date=start_date, end_date=end_date
        )

        return f"📊 Tax Report ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting tax report: {str(e)}"


@mcp.tool()
async def get_expense_report(start_date: str, end_date: str) -> str:
    try:
        result = await client.get_reports(
            report_type="expense_summary", start_date=start_date, end_date=end_date
        )

        return f"📊 Expense Report ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting expense report: {str(e)}"


@mcp.tool()
async def get_invoice_report(start_date: str, end_date: str) -> str:
    try:
        result = await client.get_reports(
            report_type="invoice_summary", start_date=start_date, end_date=end_date
        )

        return f"📊 Invoice Report ({start_date} to {end_date})\n\n{json.dumps(result, indent=2)}"
    except Exception as e:
        return f"❌ Error getting invoice report: {str(e)}"


@mcp.tool()
async def create_expense(
    amount: float,
    expense_date: str,
    vendor_id: str | None = None,
    category_id: str | None = None,
    public_notes: str | None = None,
    private_notes: str | None = None,
    tax_rate1: float | None = None,
    tax_name1: str | None = None,
) -> str:
    try:
        expense_data = {"amount": amount, "expense_date": expense_date}

        if vendor_id:
            expense_data["vendor_id"] = vendor_id
        if category_id:
            expense_data["category_id"] = category_id
        if public_notes:
            expense_data["public_notes"] = public_notes
        if private_notes:
            expense_data["private_notes"] = private_notes
        if tax_rate1 is not None:
            expense_data["tax_rate1"] = tax_rate1
        if tax_name1:
            expense_data["tax_name1"] = tax_name1

        result = await client.create_expense(expense_data)
        exp_data = result.get("data", result)
        exp = Expense(**exp_data)

        return f"✅ Expense created successfully!\nID: {exp.id}\nAmount: ${exp.amount:.2f}\nDate: {exp.expense_date}"
    except Exception as e:
        return f"❌ Error creating expense: {str(e)}"


@mcp.tool()
async def update_expense(expense_id: str, expense_data: str) -> str:
    try:
        data = json.loads(expense_data)
        result = await client.update_expense(expense_id, data)
        exp_data = result.get("data", result)
        exp = Expense(**exp_data)

        output = [f"✅ Expense updated successfully!\n"]
        output.append(f"ID: {exp.id}")
        output.append(f"Amount: ${exp.amount:.2f}")
        if exp.expense_date:
            output.append(f"Date: {exp.expense_date}")
        if exp.vendor_id:
            output.append(f"Vendor ID: {exp.vendor_id}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error updating expense: {str(e)}"


@mcp.tool()
async def create_vendor(
    name: str,
    phone: str | None = None,
    website: str | None = None,
    address1: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
    vat_number: str | None = None,
) -> str:
    try:
        vendor_data = {"name": name}

        if phone:
            vendor_data["phone"] = phone
        if website:
            vendor_data["website"] = website
        if address1:
            vendor_data["address1"] = address1
        if city:
            vendor_data["city"] = city
        if postal_code:
            vendor_data["postal_code"] = postal_code
        if vat_number:
            vendor_data["vat_number"] = vat_number

        result = await client.create_vendor(vendor_data)
        vendor_data_result = result.get("data", result)
        vendor = Vendor(**vendor_data_result)

        return f"✅ Vendor created successfully!\nID: {vendor.id}\nName: {vendor.name}"
    except Exception as e:
        return f"❌ Error creating vendor: {str(e)}"


if __name__ == "__main__":
    mcp.run()
