import pytest
from unittest.mock import AsyncMock, patch

from invoiceninja_mcp.client import InvoiceNinjaClient


@pytest.mark.asyncio
async def test_send_entity_email_posts_emails_endpoint():
    client = InvoiceNinjaClient()
    client.post = AsyncMock(return_value={"data": {"id": "pay1"}})

    await client.send_entity_email(
        entity="payment",
        entity_id="pay1",
        template="email_template_payment",
    )

    client.post.assert_awaited_once_with(
        "emails",
        json={
            "entity": "payment",
            "entity_id": "pay1",
            "template": "email_template_payment",
        },
    )


@pytest.mark.asyncio
async def test_email_payment_receipt_uses_emails_endpoint():
    client = InvoiceNinjaClient()
    client.send_entity_email = AsyncMock(return_value={"ok": True})
    client.bulk_payments = AsyncMock()

    result = await client.email_payment_receipt("abc123")

    assert result == {"ok": True}
    client.send_entity_email.assert_awaited_once_with(
        entity="payment",
        entity_id="abc123",
        template="email_template_payment",
    )
    client.bulk_payments.assert_not_awaited()


@pytest.mark.asyncio
async def test_email_payment_receipt_falls_back_to_bulk_email():
    client = InvoiceNinjaClient()
    client.send_entity_email = AsyncMock(side_effect=Exception("emails failed"))
    client.bulk_payments = AsyncMock(return_value={"data": [{"id": "abc123"}]})

    result = await client.email_payment_receipt("abc123")

    assert result["data"][0]["id"] == "abc123"
    client.bulk_payments.assert_awaited_once_with("email", ["abc123"])


@pytest.mark.asyncio
async def test_find_payments_for_invoice_uses_include_payments():
    client = InvoiceNinjaClient()
    client.get_invoice = AsyncMock(
        return_value={
            "data": {
                "id": "inv1",
                "client_id": "cli1",
                "payments": [{"id": "pay1", "number": "0019", "amount": 10}],
            }
        }
    )
    client.list_payments = AsyncMock()

    payments = await client.find_payments_for_invoice("inv1")

    assert len(payments) == 1
    assert payments[0]["id"] == "pay1"
    client.get_invoice.assert_awaited_once_with("inv1", include="payments")
    client.list_payments.assert_not_awaited()


@pytest.mark.asyncio
async def test_find_payments_for_invoice_falls_back_to_client_list():
    client = InvoiceNinjaClient()
    client.get_invoice = AsyncMock(
        return_value={"data": {"id": "inv1", "client_id": "cli1", "payments": []}}
    )
    client.list_payments = AsyncMock(
        return_value={
            "data": [
                {
                    "id": "pay_other",
                    "invoices": [{"id": "inv_other"}],
                },
                {
                    "id": "pay_match",
                    "invoices": [{"id": "inv1", "amount": 5}],
                },
            ]
        }
    )

    payments = await client.find_payments_for_invoice("inv1")

    assert [p["id"] for p in payments] == ["pay_match"]
    client.list_payments.assert_awaited_once_with(
        client_id="cli1", per_page=100, include="invoices"
    )


@pytest.mark.asyncio
async def test_email_payment_receipt_tool_resolves_invoice_payment():
    from invoiceninja_mcp import server

    fake_client = AsyncMock()
    fake_client.find_payments_for_invoice = AsyncMock(
        return_value=[
            {
                "id": "pay_old",
                "number": "0010",
                "date": "2026-01-01",
                "amount": 10,
            },
            {
                "id": "pay_new",
                "number": "0011",
                "date": "2026-08-09",
                "amount": 759.73,
                "transaction_reference": "REF123",
            },
        ]
    )
    fake_client.get_invoice = AsyncMock(
        return_value={
            "data": {
                "id": "inv1",
                "number": "FNF0027",
                "amount": 759.73,
                "balance": 0,
                "status_id": 4,
            }
        }
    )
    fake_client.email_payment_receipt = AsyncMock(return_value={"ok": True})

    with (
        patch.object(server, "client", fake_client),
        patch.object(server, "money", AsyncMock(side_effect=lambda a, c=None: f"€{a:.2f}")),
    ):
        result = await server.email_payment_receipt.fn(invoice_id="inv1")

    assert "✅ Payment receipt emailed" in result
    assert "pay_new" in result
    assert "FNF0027" in result
    assert "Only the payment receipt was sent" in result
    assert "2 payments" in result
    fake_client.email_payment_receipt.assert_awaited_once_with("pay_new")


@pytest.mark.asyncio
async def test_email_payment_receipt_tool_requires_id():
    from invoiceninja_mcp import server

    result = await server.email_payment_receipt.fn()
    assert result.startswith("❌ Provide payment_id or invoice_id")
