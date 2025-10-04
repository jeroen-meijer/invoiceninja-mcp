"""InvoiceNinja API client."""

import httpx
from typing import Any, Dict, List, Optional
from .config import settings


class InvoiceNinjaClient:
    """Async HTTP client for InvoiceNinja API."""

    def __init__(self):
        """Initialize the InvoiceNinja API client."""
        self.base_url = settings.api_url.rstrip("/")
        self.timeout = settings.invoiceninja_timeout
        self.max_retries = settings.invoiceninja_max_retries

        # Required headers for InvoiceNinja API
        self.headers = {
            "X-API-Token": settings.api_key,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the InvoiceNinja API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json: JSON body for POST/PUT requests

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPError: For HTTP errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=json
            )
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Try to get error details from response
                try:
                    error_detail = e.response.json()
                    raise Exception(f"HTTP {e.response.status_code}: {error_detail}")
                except:
                    raise e

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, json=json)

    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, json=json)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint)

    # Read-only API methods
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and authentication by listing clients."""
        return await self.get("clients?per_page=1")

    async def list_invoices(
        self,
        status: Optional[str] = None,
        client_id: Optional[str] = None,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        List invoices with optional filters.

        Args:
            status: Filter by status (draft, sent, viewed, approved, partial, paid)
            client_id: Filter by client ID
            per_page: Number of results per page
        """
        params = {"per_page": per_page}
        if status:
            params["status"] = status
        if client_id:
            params["client_id"] = client_id
        return await self.get("invoices", params=params)

    async def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get a specific invoice by ID."""
        return await self.get(f"invoices/{invoice_id}")

    async def list_expenses(
        self,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List expenses."""
        params = {"per_page": per_page}
        return await self.get("expenses", params=params)

    async def get_expense(self, expense_id: str) -> Dict[str, Any]:
        """Get a specific expense by ID."""
        return await self.get(f"expenses/{expense_id}")

    async def list_clients(self, per_page: int = 100) -> Dict[str, Any]:
        """List all clients."""
        params = {"per_page": per_page}
        return await self.get("clients", params=params)

    async def list_vendors(self, per_page: int = 100) -> Dict[str, Any]:
        """List all vendors."""
        params = {"per_page": per_page}
        return await self.get("vendors", params=params)

    async def list_expense_categories(self, per_page: int = 100) -> Dict[str, Any]:
        """List all expense categories."""
        params = {"per_page": per_page}
        return await self.get("expense_categories", params=params)

    async def get_reports(
        self,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get reports.

        Args:
            report_type: Type of report (tax_summary, expense_summary, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        """
        params = {"report_type": report_type}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self.get("reports", params=params)

    # Write operations (use with caution)
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new invoice.

        Args:
            invoice_data: Invoice data dictionary
        """
        return await self.post("invoices", json=invoice_data)

    async def create_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new expense.

        Args:
            expense_data: Expense data dictionary
        """
        return await self.post("expenses", json=expense_data)
