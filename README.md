# InvoiceNinja MCP Server

Model Context Protocol (MCP) server for InvoiceNinja v5.11.62 integration with Claude Desktop, Claude Code, and Cursor.ai.

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
- InvoiceNinja v5.11.62 instance
- API token from your InvoiceNinja admin panel

### Setup

1. **Clone or navigate to the project:**
```bash
cd in-mcp
```

2. **Install dependencies:**
```bash
poetry install
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your InvoiceNinja credentials:
```env
API_URL=https://your-instance.com/api/v1
API_KEY=your_api_token_here
```

4. **Test the connection:**
```bash
poetry run python tests/test_connection.py
```

5. **Run tests** (requires configured `.env` with API credentials):
```bash
# Run safe read-only tests (default - no data is created or modified)
poetry run pytest tests/ -v

# Run ALL tests including those that create invoices, expenses, vendors
# WARNING: This creates real data in your Invoice Ninja instance!
ALLOW_WRITE_TESTS=1 poetry run pytest tests/ -v
```

## MCP Server Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "invoiceninja": {
      "command": "poetry",
      "args": ["run", "python", "-m", "invoiceninja_mcp"],
      "cwd": "/full/path/to/in-mcp"
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
- **`create_invoice(client_id, line_items, ...)`** - Create a new invoice (line_items as JSON)
- **`update_invoice(invoice_id, invoice_data)`** - Update an invoice (JSON)
- **`clone_invoice(invoice_id)`** - Clone an existing invoice
- **`delete_invoice(invoice_id)`** - Delete an invoice (soft delete)
- **`email_invoice(invoice_id)`** - Email invoice to client
- **`mark_invoice_sent(invoice_id)`** - Mark invoice as sent
- **`mark_invoice_paid(invoice_id)`** - Mark invoice as paid

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

    # List invoices
    invoices = await client.list_invoices(status="sent", per_page=10)

    # Get specific invoice
    invoice = await client.get_invoice("invoice_id_here")

    # List clients
    clients = await client.list_clients()
```

## Project Structure

```
invoiceninja-mcp/
├── api-docs.yaml           # Invoice Ninja OpenAPI spec (reference)
├── invoiceninja_mcp/
│  ├── __init__.py
│  ├── __main__.py        # Entry point
│  ├── server.py          # FastMCP server with tools
│  ├── client.py          # InvoiceNinja API client
│  ├── config.py          # Settings management
│  └── models.py          # Pydantic models
├── tests/                     # Test suite
├── pyproject.toml             # Dependencies
├── .env                       # Your config (gitignored)
├── .env.example               # Example config
├── .gitignore
└── README.md
```

## Development

### Running Tests

Tests require a configured `.env` file with valid API credentials.

**By default, only read-only tests run**—no invoices, expenses, or vendors are created:

```bash
# Test API connection
poetry run python tests/test_connection.py

# Run safe tests (list, get, reports - no writes)
poetry run pytest tests/ -v
```

**Write tests are skipped by default** to avoid creating real data. To run them (e.g. on a demo instance):

```bash
# WARNING: Creates real invoices, expenses, vendors in your instance!
ALLOW_WRITE_TESTS=1 poetry run pytest tests/ -v
```

### Running the MCP Server

```bash
# Start the server
poetry run python -m invoiceninja_mcp

# Or with poetry
poetry run invoiceninja_mcp
```

## API Reference

A copy of the Invoice Ninja OpenAPI specification is included in this repo:

- **`api-docs.yaml`** - Full OpenAPI 3.0 spec from [Invoice Ninja v5-stable](https://github.com/invoiceninja/invoiceninja/blob/v5-stable/openapi/api-docs.yaml)

Useful links:
- [Invoice Ninja API Reference](https://invoiceninja.github.io/docs/api-reference/invoice-ninja-api-reference)
- [Clients API](https://invoiceninja.github.io/docs/api-reference/clients)
- [Invoices API](https://invoiceninja.github.io/docs/api-reference/invoices)

## API Details

### Authentication Headers

The client automatically includes:
- `X-API-Token`: Your API token
- `X-Requested-With`: XMLHttpRequest
- `Content-Type`: application/json
- `Accept`: application/json

### Invoice Status Codes

- 1 = Draft
- 2 = Sent
- 3 = Viewed
- 4 = Approved
- 5 = Partial
- 6 = Paid

### Tax Calculations

Invoices return both:
- **Amount including tax** - Full invoice total
- **Amount excluding tax** - Subtotal before tax
- **Tax amount** - Total tax

## Troubleshooting

### 403 Forbidden Error

- Verify your API token in InvoiceNinja admin panel
- Check that the token has appropriate permissions
- Ensure API_URL includes `/api/v1`

### Connection Timeout

- Increase `INVOICENINJA_TIMEOUT` in `.env`
- Check your InvoiceNinja instance is accessible

### Validation Errors

- Ensure you're using InvoiceNinja v5.11.62 or compatible version
- Check API responses match expected data structure

## License

MIT

## Credits

Built with:
- [FastMCP](https://gofastmcp.com/) - MCP server framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [InvoiceNinja](https://invoiceninja.com/) - Invoice management platform

## Contributing

Contributions welcome! Please ensure:
- All tests pass
- Code follows existing patterns
- Documentation is updated
- Security best practices are followed

## Security

- Never commit `.env` file
- Keep API tokens secure
- Use HTTPS for InvoiceNinja instance
- Review API token permissions regularly
