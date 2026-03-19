# InvoiceNinja MCP Server

Model Context Protocol (MCP) server for InvoiceNinja v5 integration with Claude Desktop, Claude Code, and Cursor.ai.

## Features

**✅ READ-ONLY Operations (Tested & Working)**
- 📄 List and view invoices with tax calculations
- 💳 List and view expenses
- 👥 List clients, vendors, and expense categories
- 📊 Generate tax reports (quarterly and custom date ranges)
- 📈 Invoice and expense reports

**✏️ WRITE Operations**
- Create clients, invoices, expenses, vendors
- Update clients, invoices, expenses
- Delete clients and invoices (soft delete)
- Clone invoices
- Send invoice emails

## Installation

### Prerequisites
- Python 3.10+
- Poetry (recommended) or pip
- InvoiceNinja v5 instance
- API token from your InvoiceNinja admin panel

### Setup

1. **Install dependencies:**
```bash
poetry install
```

2. **Configure credentials** (e.g. in a `.env` file):
```env
API_URL=https://your-instance.com/api/v1
API_KEY=your_api_token_here
```

3. **Verify connection** (optional):
```bash
poetry run python tests/test_connection.py
```

4. **Run tests** (optional, requires configured credentials):
```bash
# Run safe read-only tests (default - no data is created or modified)
poetry run pytest tests/ -v

# Run ALL tests including those that create invoices, expenses, vendors
# WARNING: This creates real data in your Invoice Ninja instance!
ALLOW_WRITE_TESTS=1 poetry run pytest tests/ -v
```

## MCP Server Configuration

### Claude Desktop

Add to your MCP config:

```json
{
  "mcpServers": {
    "invoiceninja": {
      "command": "poetry",
      "args": ["run", "python", "-m", "invoiceninja_mcp"],
      "cwd": "/path/to/invoiceninja-mcp"
    }
  }
}
```

### Cursor.ai

Add similar configuration in Cursor's MCP settings.

### Claude Code

The MCP server should be automatically detected when running in the project directory.

## Available Tools

### 📊 Utility Tools

- **`test_connection()`** - Test API connection and authentication
- **`list_vendors(per_page=100)`** - List all vendors
- **`search_vendors(search_term)`** - Search vendors by name
- **`list_expense_categories(per_page=100)`** - List expense categories

### 👥 Client Tools

- **`list_clients(per_page=100)`** - List all clients
- **`create_client(name, email?, phone?, ...)`** - Create a new client
- **`update_client(client_id, client_data)`** - Update a client (JSON)
- **`delete_client(client_id)`** - Delete a client (soft delete)

### 📄 Invoice Tools

- **`list_invoices(status?, client_id?, per_page=20)`** - List invoices with filters
  - Status: draft, sent, viewed, approved, partial, paid
- **`get_invoice(invoice_id)`** - Get detailed invoice information
  - Shows amounts including/excluding tax
  - Line items breakdown
  - Payment status
- **`get_invoice_status(invoice_id)`** - Get current invoice status
- **`get_latest_invoice_for_client(client_id)`** - Get the most recent invoice for a client
- **`create_invoice(client_id, line_items, ...)`** - Create a new invoice (line_items as JSON)
- **`update_invoice(invoice_id, invoice_data)`** - Update an invoice (JSON)
- **`clone_invoice(invoice_id)`** - Clone an existing invoice
- **`delete_invoice(invoice_id)`** - Delete an invoice (soft delete)
- **`email_invoice(invoice_id)`** - Email invoice to client
- **`mark_invoice_sent(invoice_id)`** - Mark invoice as sent
- **`mark_invoice_paid(invoice_id)`** - Mark invoice as paid
- **`record_invoice_payment_and_send_receipt(invoice_id, payment_date?, transaction_reference?)`** - Record full bank transfer payment and email receipt to client
- **`preview_invoice_pdf(invoice_id)`** - Get base64-encoded PDF preview
- **`get_invoice_preview_url(invoice_id)`** - Get URL to preview invoice in browser

### 💳 Expense Tools

- **`list_expenses(per_page=20)`** - List expenses
- **`get_expense(expense_id)`** - Get detailed expense information

### 📊 Report Tools

- **`get_tax_report_quarterly(year, quarter)`** - Get tax report for Q1/Q2/Q3/Q4
  - Example: `get_tax_report_quarterly(2024, 1)` for Q1 2024
- **`get_tax_report_custom(start_date, end_date)`** - Custom date range tax report
  - Dates in YYYY-MM-DD format
- **`get_expense_report(start_date, end_date)`** - Expense summary report
- **`get_invoice_report(start_date, end_date)`** - Invoice summary report

## Usage Examples

### With Claude Desktop

```
List all invoices from this month

Show me invoices that are still unpaid

Get the tax report for Q3 2024

What's the status of invoice ID abc123?

List all expenses from January 2024
```

### Programmatic Usage

```python
from invoiceninja_mcp.client import InvoiceNinjaClient

async def example():
    client = InvoiceNinjaClient()
    invoices = await client.list_invoices(status="sent", per_page=10)
    invoice = await client.get_invoice("invoice_id_here")
    clients = await client.list_clients()
```

## Running the MCP Server

```bash
poetry run python -m invoiceninja_mcp
```

## API Reference

[Invoice Ninja API docs](https://invoiceninja.github.io/docs/api-reference/invoice-ninja-api-reference) for detailed endpoint reference.

## Troubleshooting

### 403 Forbidden Error

- Verify your API token in InvoiceNinja admin panel
- Check that the token has appropriate permissions
- Ensure `API_URL` includes `/api/v1`

### Connection Timeout

- Increase `INVOICENINJA_TIMEOUT`
- Check your InvoiceNinja instance is accessible

### Validation Errors

- Ensure your InvoiceNinja version is compatible with the API
- Verify request data format matches API expectations

## License

MIT

## Credits

Built with:
- [FastMCP](https://gofastmcp.com/) - MCP server framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [InvoiceNinja](https://invoiceninja.com/) - Invoice management platform

## Contributing

Contributions welcome. Ensure tests pass and security best practices are followed.

## Security

- Do not commit credentials
- Keep API tokens secure
- Use HTTPS for InvoiceNinja instance
- Review API token permissions regularly
