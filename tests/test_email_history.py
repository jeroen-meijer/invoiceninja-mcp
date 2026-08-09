import pytest
from unittest.mock import AsyncMock, patch

from invoiceninja_mcp.client import InvoiceNinjaClient
from invoiceninja_mcp.server import _format_email_history_entries


def test_format_email_history_entries_empty():
    assert _format_email_history_entries([]) == ["No email history entries found."]


def test_format_email_history_entries_with_events():
    lines = _format_email_history_entries(
        [
            {
                "entity": "invoice",
                "entity_id": "inv1",
                "subject": "Invoice FNF0025",
                "recipient": "a@b.com",
                "events": [
                    {"type": "delivered", "date": "2026-08-09", "recipient": "a@b.com"}
                ],
            }
        ]
    )
    text = "\n".join(lines)
    assert "Found 1 email history record" in text
    assert "invoice (inv1)" in text
    assert "delivered @ 2026-08-09" in text


@pytest.mark.asyncio
async def test_get_client_email_history_posts_route():
    client = InvoiceNinjaClient()
    client.post = AsyncMock(return_value=[{"entity": "invoice", "events": [{"type": "sent"}]}])

    result = await client.get_client_email_history("cli1")

    client.post.assert_awaited_once_with("emails/clientHistory/cli1")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_entity_email_history_posts_payload():
    client = InvoiceNinjaClient()
    client.post = AsyncMock(return_value=[])

    await client.get_entity_email_history("invoice", "inv1")

    client.post.assert_awaited_once_with(
        "emails/entityHistory",
        json={"entity": "invoice", "entity_id": "inv1"},
    )


@pytest.mark.asyncio
async def test_get_client_email_history_tool():
    from invoiceninja_mcp import server

    fake_client = AsyncMock()
    fake_client.get_client_email_history = AsyncMock(
        return_value=[
            {
                "entity": "payment",
                "entity_id": "pay1",
                "subject": "Payment received",
                "events": [{"type": "delivered", "date": "2026-07-21"}],
            }
        ]
    )

    with patch.object(server, "client", fake_client):
        result = await server.get_client_email_history.fn("cli1")

    assert "payment (pay1)" in result
    assert "delivered" in result


@pytest.mark.asyncio
async def test_get_entity_email_history_tool_rejects_payment():
    from invoiceninja_mcp import server

    result = await server.get_entity_email_history.fn("payment", "pay1")
    assert result.startswith("❌ Unsupported entity")


@pytest.mark.asyncio
async def test_get_invoice_email_history_tool_includes_invitations():
    from invoiceninja_mcp import server

    fake_client = AsyncMock()
    fake_client.get_invoice = AsyncMock(
        return_value={
            "data": {
                "id": "inv1",
                "number": "FNF0025",
                "amount": 54.5,
                "balance": 0,
                "status_id": 4,
                "invitations": [
                    {
                        "id": "invit1",
                        "sent_date": "2026-07-20",
                        "email_status": "delivered",
                        "message_id": "mid-1",
                    }
                ],
            }
        }
    )
    fake_client.get_entity_email_history = AsyncMock(return_value=[])

    with patch.object(server, "client", fake_client):
        result = await server.get_invoice_email_history.fn("inv1")

    assert "FNF0025" in result
    assert "Email status: delivered" in result
    assert "No SystemLog history entries" in result
    fake_client.get_entity_email_history.assert_awaited_once_with("invoice", "inv1")
