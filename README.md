# InvoiceNinja MCP Server

Model Context Protocol (MCP) server for InvoiceNinja v5.11.62 integration with Claude Desktop, Claude Code, and Cursor.ai.

## Features

**✅ READ-ONLY Operations (Tested & Working)**
- 📄 List and view invoices with tax calculations
- 💳 List and view expenses
- 👥 List clients, vendors, and expense categories
- 📊 Generate tax reports (quarterly and custom date ranges)
- 📈 Invoice and expense reports

**🔒 WRITE Operations (To Be Implemented)**
- Create invoices and expenses
- Update invoices and expenses
- Clone invoices and expenses
- Send invoice emails
- Upload expense documents

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
poetry run python test_connection.py
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
- **`list_clients(per_page=100)`** - List all clients
- **`list_vendors(per_page=100)`** - List all vendors
- **`list_expense_categories(per_page=100)`** - List expense categories

### 📄 Invoice Tools (Read-Only)

- **`list_invoices(status?, client_id?, per_page=20)`** - List invoices with filters
  - Status: draft, sent, viewed, approved, partial, paid
- **`get_invoice(invoice_id)`** - Get detailed invoice information
  - Shows amounts including/excluding tax
  - Line items breakdown
  - Payment status
- **`get_invoice_status(invoice_id)`** - Get current invoice status

### 💳 Expense Tools (Read-Only)

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
in-mcp/
└── invoiceninja_mcp/
│  ├── __init__.py
│  ├── __main__.py        # Entry point
│  ├── server.py          # FastMCP server with tools
│  ├── client.py          # InvoiceNinja API client
│  ├── config.py          # Settings management
│  └── models.py          # Pydantic models
├── pyproject.toml             # Dependencies
├── .env                       # Your config (gitignored)
├── .env.example               # Example config
├── .gitignore
└── README.md
```

## Development

### Running Tests

```bash
# Test API connection
poetry run python test_connection.py

# Test all MCP tools
poetry run python test_mcp_tools.py
```

### Running the MCP Server

```bash
# Start the server
poetry run python -m invoiceninja_mcp

# Or with poetry
poetry run invoiceninja_mcp
```

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
