import httpx
from typing import Any, Dict, List, Optional
from .config import settings


class InvoiceNinjaClient:
    def __init__(self):
        self.base_url = settings.api_url.rstrip("/")
        self.timeout = settings.invoiceninja_timeout
        self.max_retries = settings.invoiceninja_max_retries
        self.headers = {
            "X-API-Token": settings.api_key,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method, url=url, headers=self.headers, params=params, json=json
            )
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                try:
                    error_detail = e.response.json()
                    raise Exception(f"HTTP {e.response.status_code}: {error_detail}")
                except:
                    raise e

    async def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._make_request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self._make_request("POST", endpoint, json=json, params=params)

    async def put(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._make_request("PUT", endpoint, json=json)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", endpoint)

    async def test_connection(self) -> Dict[str, Any]:
        return await self.get("clients?per_page=1")

    async def list_invoices(
        self,
        status: Optional[str] = "Active",
        client_id: Optional[str] = None,
        per_page: int = 20,
        sort: str = "date|desc",
        include: Optional[str] = None,
        without_deleted_clients: bool = True,
    ) -> Dict[str, Any]:
        params = {
            "per_page": per_page,
            "sort": sort,
            "without_deleted_clients": "true" if without_deleted_clients else "false",
        }
        if status:
            params["status"] = status
        if client_id:
            params["client_id"] = client_id
        if include:
            params["include"] = include
        return await self.get("invoices", params=params)

    async def get_invoice(
        self, invoice_id: str, include: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {"include": include} if include else None
        return await self.get(f"invoices/{invoice_id}", params=params)

    async def list_expenses(
        self,
        per_page: int = 20,
        sort: str = "expense_date|desc",
        include: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        vendor_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"per_page": per_page, "sort": sort}
        if include:
            params["include"] = include
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if vendor_id:
            params["vendor_id"] = vendor_id
        return await self.get("expenses", params=params)

    async def get_expense(self, expense_id: str) -> Dict[str, Any]:
        return await self.get(f"expenses/{expense_id}")

    async def list_clients(
        self,
        per_page: int = 100,
        sort: str = "name|asc",
        include: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"per_page": per_page, "sort": sort}
        if include:
            params["include"] = include
        return await self.get("clients", params=params)

    async def get_client(
        self, client_id: str, include: Optional[str] = "contacts"
    ) -> Dict[str, Any]:
        params = {"include": include} if include else None
        return await self.get(f"clients/{client_id}", params=params)

    async def list_vendors(
        self,
        per_page: int = 100,
        sort: str = "name|asc",
        include: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"per_page": per_page, "sort": sort}
        if include:
            params["include"] = include
        return await self.get("vendors", params=params)

    async def list_expense_categories(
        self,
        per_page: int = 100,
        sort: str = "name|asc",
        include: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"per_page": per_page, "sort": sort}
        if include:
            params["include"] = include
        return await self.get("expense_categories", params=params)

    async def get_reports(
        self,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {"report_type": report_type}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self.get("reports", params=params)

    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("invoices", json=invoice_data)

    async def create_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("expenses", json=expense_data)

    async def create_vendor(self, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("vendors", json=vendor_data)

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("clients", json=client_data)

    async def update_client(
        self, client_id: str, client_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.put(f"clients/{client_id}", json=client_data)

    async def delete_client(self, client_id: str) -> Dict[str, Any]:
        return await self.delete(f"clients/{client_id}")

    async def delete_invoice(self, invoice_id: str) -> Dict[str, Any]:
        return await self.delete(f"invoices/{invoice_id}")

    async def update_invoice(
        self, invoice_id: str, invoice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.put(f"invoices/{invoice_id}", json=invoice_data)

    async def update_expense(
        self, expense_id: str, expense_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await self.put(f"expenses/{expense_id}", json=expense_data)

    async def clone_invoice(self, invoice_id: str) -> Dict[str, Any]:
        return await self.post("invoices/bulk", json={"action": "clone", "ids": [invoice_id]})

    async def bulk_invoices(
        self, action: str, ids: List[str]
    ) -> Dict[str, Any]:
        return await self.post("invoices/bulk", json={"action": action, "ids": ids})

    async def download_invoice_pdf(self, invoice_id: str) -> bytes:
        url = f"{self.base_url}/invoices/{invoice_id}/download"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content

    async def create_payment(
        self,
        client_id: str,
        amount: float,
        invoices: List[Dict[str, Any]],
        payment_date: str,
        type_id: str = "1",
        transaction_reference: Optional[str] = None,
        email_receipt: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a payment. type_id '1' = Bank Transfer.
        When invoices are linked, the payment is applied and invoices are marked paid.
        """
        request_params = {}
        if email_receipt:
            request_params["email_receipt"] = "true"

        payload: Dict[str, Any] = {
            "client_id": client_id,
            "amount": amount,
            "date": payment_date,
            "type_id": type_id,
            "invoices": invoices,
        }
        if transaction_reference:
            payload["transaction_reference"] = transaction_reference

        return await self.post("payments", json=payload, params=request_params or None)

    async def list_payments(
        self,
        client_id: Optional[str] = None,
        per_page: int = 20,
        sort: str = "date|desc",
        include: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"per_page": per_page, "sort": sort}
        if client_id:
            params["client_id"] = client_id
        if include:
            params["include"] = include
        return await self.get("payments", params=params)

    async def get_payment(
        self, payment_id: str, include: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {"include": include} if include else None
        return await self.get(f"payments/{payment_id}", params=params)

    async def bulk_payments(
        self, action: str, ids: List[str]
    ) -> Dict[str, Any]:
        return await self.post("payments/bulk", json={"action": action, "ids": ids})

    async def send_entity_email(
        self,
        entity: str,
        entity_id: str,
        template: str,
        subject: Optional[str] = None,
        body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an entity email via POST /emails (Invoice Ninja v5).

        For payment receipts use entity='payment' and template='email_template_payment'.
        See OpenAPI: POST /api/v1/emails (operationId sendEmailTemplate).
        """
        payload: Dict[str, Any] = {
            "entity": entity,
            "entity_id": entity_id,
            "template": template,
        }
        if subject is not None:
            payload["subject"] = subject
        if body is not None:
            payload["body"] = body
        return await self.post("emails", json=payload)

    async def email_payment_receipt(self, payment_id: str) -> Dict[str, Any]:
        """
        Email only the payment receipt to client contacts.

        Prefers POST /emails with email_template_payment (documented v5 API).
        Falls back to payments/bulk action 'email' (PaymentService::sendEmail).
        """
        try:
            return await self.send_entity_email(
                entity="payment",
                entity_id=payment_id,
                template="email_template_payment",
            )
        except Exception:
            return await self.bulk_payments("email", [payment_id])

    async def find_payments_for_invoice(
        self, invoice_id: str
    ) -> List[Dict[str, Any]]:
        """Return payments applied to an invoice (newest first when sortable)."""
        inv_result = await self.get_invoice(invoice_id, include="payments")
        inv_data = inv_result.get("data", inv_result)
        payments = inv_data.get("payments") or []
        if payments:
            return payments

        client_id = inv_data.get("client_id")
        if not client_id:
            return []

        listed = await self.list_payments(
            client_id=client_id, per_page=100, include="invoices"
        )
        matched: List[Dict[str, Any]] = []
        for payment in listed.get("data", []):
            linked_invoices = payment.get("invoices") or []
            for linked in linked_invoices:
                linked_id = linked.get("id") if isinstance(linked, dict) else None
                if linked_id == invoice_id:
                    matched.append(payment)
                    break
        return matched

    async def get_client_email_history(self, client_id: str) -> Any:
        """
        Mail delivery history for a client.

        POST /api/v1/emails/clientHistory/{client}
        Returns SystemLog mail histories that include delivery events.
        """
        return await self.post(f"emails/clientHistory/{client_id}")

    async def get_entity_email_history(
        self, entity: str, entity_id: str
    ) -> Any:
        """
        Mail delivery history for an entity.

        POST /api/v1/emails/entityHistory
        entity: invoice | quote | credit | recurring_invoice | purchase_order
        (payment is not supported by Invoice Ninja's EntityEmailHistoryRequest)
        """
        return await self.post(
            "emails/entityHistory",
            json={"entity": entity, "entity_id": entity_id},
        )
