# Invoice Ninja MCP - Write Operations Implementation Guide

## Overview

This document provides everything needed to implement write operations (create/update clients and invoices) for the Invoice Ninja MCP server at https://github.com/a-wiseguy/invoiceninja-mcp.

## Current State

### What's Already Working

The repository currently supports:
- ✅ Read operations for invoices, expenses, clients, vendors
- ✅ Some write operations: `create_expense`, `create_vendor`, `update_expense`, `update_invoice`, `clone_invoice`, `email_invoice`
- ✅ HTTP client with POST/PUT/DELETE methods already implemented
- ✅ Authentication headers properly configured

### What Needs Implementation

- ❌ `create_client` MCP tool (client method exists but not exposed)
- ❌ `create_invoice` MCP tool (client method exists but not exposed)
- ❌ Additional client operations (update_client, delete_client)
- ❌ Additional invoice operations (delete_invoice)

## Architecture Overview

The codebase has three main components:

1. **`client.py`** - HTTP client that makes API calls to Invoice Ninja
2. **`server.py`** - FastMCP server that exposes tools to LLMs
3. **`models.py`** - Pydantic models for data validation

## Implementation Tasks

### Task 1: Add Create Client Tool

**File: `invoiceninja_mcp/server.py`**

Add this tool function (follow the pattern of `create_vendor`):

```python
@mcp.tool()
async def create_client(
    name: str,
    email: str | None = None,
    phone: str | None = None,
    website: str | None = None,
    address1: str | None = None,
    address2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postal_code: str | None = None,
    country_id: str | None = None,
    vat_number: str | None = None,
    id_number: str | None = None,
    public_notes: str | None = None,
    private_notes: str | None = None,
) -> str:
    """
    Creates a new client in Invoice Ninja.
    
    Args:
        name: Client name (required)
        email: Client email address
        phone: Client phone number
        website: Client website URL
        address1: Address line 1
        address2: Address line 2
        city: City
        state: State/Province
        postal_code: Postal/ZIP code
        country_id: Country ID (numeric string)
        vat_number: VAT/Tax number
        id_number: Client ID number
        public_notes: Notes visible to client
        private_notes: Internal notes
    
    Returns:
        Success message with client details
    """
    try:
        client_data = {"name": name}

        # Add optional fields if provided
        if email:
            client_data["email"] = email
        if phone:
            client_data["phone"] = phone
        if website:
            client_data["website"] = website
        if address1:
            client_data["address1"] = address1
        if address2:
            client_data["address2"] = address2
        if city:
            client_data["city"] = city
        if state:
            client_data["state"] = state
        if postal_code:
            client_data["postal_code"] = postal_code
        if country_id:
            client_data["country_id"] = country_id
        if vat_number:
            client_data["vat_number"] = vat_number
        if id_number:
            client_data["id_number"] = id_number
        if public_notes:
            client_data["public_notes"] = public_notes
        if private_notes:
            client_data["private_notes"] = private_notes

        result = await client.create_client(client_data)
        client_result = result.get("data", result)
        c = Client(**client_result)

        output = [f"✅ Client created successfully!\n"]
        output.append(f"ID: {c.id}")
        output.append(f"Name: {c.name}")
        if c.email:
            output.append(f"Email: {c.email}")
        if c.phone:
            output.append(f"Phone: {c.phone}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error creating client: {str(e)}"
```

**File: `invoiceninja_mcp/client.py`**

Add this method (if not already present):

```python
async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
    return await self.post("clients", json=client_data)
```

### Task 2: Add Create Invoice Tool

**File: `invoiceninja_mcp/server.py`**

Add this tool function:

```python
@mcp.tool()
async def create_invoice(
    client_id: str,
    line_items: str,
    invoice_date: str | None = None,
    due_date: str | None = None,
    po_number: str | None = None,
    discount: float | None = None,
    partial: float | None = None,
    public_notes: str | None = None,
    private_notes: str | None = None,
    terms: str | None = None,
    footer: str | None = None,
) -> str:
    """
    Creates a new invoice in Invoice Ninja.
    
    Args:
        client_id: The client ID (required)
        line_items: JSON string of line items array. Each item should have:
                   - product_key: Product/service name
                   - notes: Description
                   - cost: Unit price
                   - quantity: Quantity
                   - tax_name1: Tax name (optional)
                   - tax_rate1: Tax rate (optional)
        invoice_date: Invoice date (YYYY-MM-DD format)
        due_date: Due date (YYYY-MM-DD format)
        po_number: Purchase order number
        discount: Discount amount
        partial: Partial payment amount
        public_notes: Notes visible to client
        private_notes: Internal notes
        terms: Payment terms
        footer: Invoice footer text
    
    Returns:
        Success message with invoice details
        
    Example line_items JSON:
    [
        {
            "product_key": "Consulting",
            "notes": "Software consulting services",
            "cost": 150.00,
            "quantity": 8,
            "tax_name1": "VAT",
            "tax_rate1": 21
        }
    ]
    """
    try:
        import json
        
        # Parse line items JSON
        try:
            items = json.loads(line_items)
        except json.JSONDecodeError:
            return "❌ Error: line_items must be valid JSON array"

        invoice_data = {
            "client_id": client_id,
            "line_items": items,
        }

        # Add optional fields
        if invoice_date:
            invoice_data["date"] = invoice_date
        if due_date:
            invoice_data["due_date"] = due_date
        if po_number:
            invoice_data["po_number"] = po_number
        if discount is not None:
            invoice_data["discount"] = discount
        if partial is not None:
            invoice_data["partial"] = partial
        if public_notes:
            invoice_data["public_notes"] = public_notes
        if private_notes:
            invoice_data["private_notes"] = private_notes
        if terms:
            invoice_data["terms"] = terms
        if footer:
            invoice_data["footer"] = footer

        result = await client.create_invoice(invoice_data)
        inv_data = result.get("data", result)
        inv = Invoice(**inv_data)

        output = [f"✅ Invoice created successfully!\n"]
        output.append(f"Invoice #{inv.get_invoice_number()} (ID: {inv.id})")
        output.append(f"Status: {inv.get_status_name()}")
        output.append(f"Total (incl. tax): ${inv.get_amount_incl_tax():.2f}")
        output.append(f"Total (excl. tax): ${inv.get_amount_excl_tax():.2f}")
        if inv.date:
            output.append(f"Date: {inv.date}")
        if inv.due_date:
            output.append(f"Due Date: {inv.due_date}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error creating invoice: {str(e)}"
```

Note: The `create_invoice` method already exists in `client.py`, so no changes needed there.

### Task 3: Add Update Client Tool

**File: `invoiceninja_mcp/server.py`**

```python
@mcp.tool()
async def update_client(client_id: str, client_data: str) -> str:
    """
    Updates an existing client.
    
    Args:
        client_id: The client ID to update
        client_data: JSON string with fields to update
        
    Returns:
        Success message with updated client details
    """
    try:
        import json

        data = json.loads(client_data)
        result = await client.update_client(client_id, data)
        client_result = result.get("data", result)
        c = Client(**client_result)

        output = [f"✅ Client updated successfully!\n"]
        output.append(f"ID: {c.id}")
        output.append(f"Name: {c.name}")
        if c.email:
            output.append(f"Email: {c.email}")
        if c.phone:
            output.append(f"Phone: {c.phone}")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Error updating client: {str(e)}"
```

**File: `invoiceninja_mcp/client.py`**

```python
async def update_client(
    self, client_id: str, client_data: Dict[str, Any]
) -> Dict[str, Any]:
    return await self.put(f"clients/{client_id}", json=client_data)
```

### Task 4: Add Delete Operations (Optional)

**File: `invoiceninja_mcp/server.py`**

```python
@mcp.tool()
async def delete_client(client_id: str) -> str:
    """
    Deletes a client (soft delete).
    
    Args:
        client_id: The client ID to delete
        
    Returns:
        Success or error message
    """
    try:
        result = await client.delete_client(client_id)
        return f"✅ Client {client_id} deleted successfully!"
    except Exception as e:
        return f"❌ Error deleting client: {str(e)}"


@mcp.tool()
async def delete_invoice(invoice_id: str) -> str:
    """
    Deletes an invoice (soft delete).
    
    Args:
        invoice_id: The invoice ID to delete
        
    Returns:
        Success or error message
    """
    try:
        result = await client.delete_invoice(invoice_id)
        return f"✅ Invoice {invoice_id} deleted successfully!"
    except Exception as e:
        return f"❌ Error deleting invoice: {str(e)}"
```

**File: `invoiceninja_mcp/client.py`**

```python
async def delete_client(self, client_id: str) -> Dict[str, Any]:
    return await self.delete(f"clients/{client_id}")

async def delete_invoice(self, invoice_id: str) -> Dict[str, Any]:
    return await self.delete(f"invoices/{invoice_id}")
```

## Invoice Ninja API Reference

### Official Documentation Links

1. **Main API Reference**: https://invoiceninja.github.io/docs/api-reference/invoice-ninja-api-reference
2. **Clients API**: https://invoiceninja.github.io/docs/api-reference/clients
3. **Invoices API**: https://invoiceninja.github.io/docs/api-reference/invoices
4. **Expenses API**: https://invoiceninja.github.io/docs/api-reference/expenses
5. **OpenAPI Spec**: https://raw.githubusercontent.com/invoiceninja/invoiceninja/v5-stable/openapi/api-docs.yaml
6. **Developer Guide**: https://invoiceninja.github.io/docs/developer-guide

### API Endpoints

#### Clients
- `GET /api/v1/clients` - List clients
- `POST /api/v1/clients` - Create client
- `GET /api/v1/clients/{id}` - Get client
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client
- `POST /api/v1/clients/bulk` - Bulk operations

#### Invoices
- `GET /api/v1/invoices` - List invoices
- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices/{id}` - Get invoice
- `PUT /api/v1/invoices/{id}` - Update invoice
- `DELETE /api/v1/invoices/{id}` - Delete invoice
- `POST /api/v1/invoices/bulk` - Bulk operations (email, mark sent, etc.)

### Authentication

All requests require these headers (already configured in `client.py`):
```python
{
    "X-API-Token": "your_api_token",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
```

### Request/Response Format

#### Create Client Request
```json
POST /api/v1/clients
{
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1-555-0123",
    "address1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country_id": "840",
    "vat_number": "VAT123456",
    "public_notes": "Important client",
    "private_notes": "Internal notes here"
}
```

#### Create Invoice Request
```json
POST /api/v1/invoices
{
    "client_id": "abc123",
    "date": "2024-01-15",
    "due_date": "2024-02-15",
    "po_number": "PO-2024-001",
    "public_notes": "Thank you for your business",
    "terms": "Net 30",
    "line_items": [
        {
            "product_key": "Consulting",
            "notes": "Software development services",
            "cost": 150.00,
            "quantity": 40,
            "tax_name1": "VAT",
            "tax_rate1": 21
        },
        {
            "product_key": "Hosting",
            "notes": "Monthly hosting fee",
            "cost": 50.00,
            "quantity": 1,
            "tax_name1": "VAT",
            "tax_rate1": 21
        }
    ]
}
```

#### Typical Response
```json
{
    "data": {
        "id": "xyz789",
        "name": "Acme Corp",
        "email": "contact@acme.com",
        "balance": 0,
        "created_at": 1234567890,
        "updated_at": 1234567890,
        // ... more fields
    }
}
```

## Data Models Reference

### Client Model (from models.py)

Key fields already defined:
```python
class Client(BaseModel):
    id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address1: str | None = None
    address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country_id: str | None = None
    balance: float = 0
    # ... more fields
```

### Invoice Model (from models.py)

Key fields already defined:
```python
class Invoice(BaseModel):
    id: str
    client_id: str | None = None
    number: str | None = None
    amount: float = 0
    balance: float = 0
    status_id: int | None = None
    date: str | None = None
    due_date: str | None = None
    line_items: List[InvoiceLineItem] = []
    total_taxes: float | None = None
    # ... more fields
```

### Invoice Line Item Model

```python
class InvoiceLineItem(BaseModel):
    product_key: str | None = None
    notes: str | None = None
    cost: float | None = None
    quantity: float | None = None
    tax_name1: str | None = None
    tax_rate1: float | None = None
    line_total: float | None = None
```

## Testing

### Test Connection
```bash
poetry run python test_connection.py
```

### Test MCP Tools
```bash
poetry run python test_mcp_tools.py
```

### Manual Testing with Claude Desktop

Add to `claude_desktop_config.json`:
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

Then test with prompts like:
- "Create a new client named 'Test Corp' with email test@example.com"
- "Create an invoice for client ID abc123 with one line item for consulting services"

## Error Handling

Common errors to handle:

1. **403 Forbidden** - Invalid API token or insufficient permissions
2. **422 Unprocessable Entity** - Validation errors (missing required fields, invalid format)
3. **404 Not Found** - Client/invoice ID doesn't exist
4. **400 Bad Request** - Malformed request data

**Common cause of 422 on create_invoice:** Partial date strings like `"2026"` instead of full `YYYY-MM-DD` (e.g. `"2026-02-16"`). The API rejects invalid date formats. **Remedy:** Use full dates or omit `invoice_date`/`due_date` to let the API use defaults.

The existing code already handles these via the `_make_request` method in `client.py`.

## Invoice Status Codes

Reference for invoice statuses:
- 1 = Draft
- 2 = Sent
- 3 = Viewed
- 4 = Approved
- 5 = Partial
- 6 = Paid

## Country IDs

Common country IDs for the `country_id` field:
- 840 = United States
- 826 = United Kingdom
- 124 = Canada
- 276 = Germany
- 528 = Netherlands
- 250 = France

Full list available in Invoice Ninja's static data endpoint.

## Best Practices

1. **Validation**: Always validate JSON input before passing to API
2. **Error Messages**: Provide clear, actionable error messages to users
3. **Required Fields**: Client name is required; invoice needs client_id and line_items
4. **Date Format**: Use full YYYY-MM-DD format for all dates (e.g. `2026-02-16`). **Never** use partial formats like `"2026"` or `"2026-02"`—they cause 422 errors. When unsure, omit date params to use API defaults.
5. **Decimal Precision**: Use 2 decimal places for monetary amounts
6. **Testing**: Test with the demo API first (https://demo.invoiceninja.com)

## Development Workflow

1. Clone the repository
2. Install dependencies: `poetry install`
3. Copy `.env.example` to `.env` and add your API credentials
4. Implement the functions above
5. Test with `poetry run python test_connection.py`
6. Test MCP tools with Claude Desktop
7. Submit PR to the original repository

## Additional Resources

- **Repository**: https://github.com/a-wiseguy/invoiceninja-mcp
- **FastMCP Documentation**: https://gofastmcp.com/
- **Invoice Ninja Forum**: https://forum.invoiceninja.com
- **Invoice Ninja Slack**: https://invoiceninja.slack.com

## Summary

The implementation is straightforward because:
- ✅ HTTP client infrastructure exists
- ✅ Authentication is configured
- ✅ Similar write operations already work (expenses, vendors)
- ✅ API is well-documented and stable
- ✅ Data models are already defined

Main work involves:
1. Adding 4-5 new tool functions to `server.py`
2. Adding 2-3 new methods to `client.py`
3. Testing the new functionality

Estimated effort: 2-4 hours for a developer familiar with Python and REST APIs.
