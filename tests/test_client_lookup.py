import pytest
from unittest.mock import AsyncMock, patch

from invoiceninja_mcp.client import InvoiceNinjaClient
from invoiceninja_mcp.models import Client
from invoiceninja_mcp.server import _contact_emails, _format_contact_lines


def test_contact_emails_from_contacts():
    emails = _contact_emails(
        {
            "contacts": [
                {"email": "a@example.com"},
                {"email": "b@example.com"},
                {"email": "a@example.com"},
            ]
        }
    )
    assert emails == ["a@example.com", "b@example.com"]


def test_contact_emails_from_client_model():
    c = Client(
        id="cli1",
        email="top@example.com",
        contacts=[{"email": "top@example.com"}, {"email": "other@example.com"}],
    )
    assert _contact_emails(c) == ["top@example.com", "other@example.com"]


def test_format_contact_lines():
    lines = _format_contact_lines(
        [
            {
                "first_name": "Jana",
                "last_name": "Muradova",
                "email": "finance@factionevents.nl",
                "send_email": True,
            }
        ]
    )
    assert lines == ["  • Jana Muradova: finance@factionevents.nl [send]"]


@pytest.mark.asyncio
async def test_get_client_requests_contacts():
    client = InvoiceNinjaClient()
    client.get = AsyncMock(return_value={"data": {"id": "cli1", "name": "Test"}})

    await client.get_client("cli1")

    client.get.assert_awaited_once_with(
        "clients/cli1", params={"include": "contacts"}
    )


@pytest.mark.asyncio
async def test_list_clients_tool_includes_emails():
    from invoiceninja_mcp import server

    fake_client = AsyncMock()
    fake_client.list_clients = AsyncMock(
        return_value={
            "data": [
                {
                    "id": "QbY6xop9dz",
                    "name": "Faction Events",
                    "balance": 0,
                    "contacts": [
                        {
                            "first_name": "Jana",
                            "email": "finance@factionevents.nl",
                            "send_email": True,
                        }
                    ],
                }
            ]
        }
    )

    with (
        patch.object(server, "client", fake_client),
        patch.object(server, "money", AsyncMock(side_effect=lambda a, c=None: f"€{a}")),
    ):
        result = await server.list_clients.fn()

    assert "Faction Events" in result
    assert "finance@factionevents.nl" in result
    fake_client.list_clients.assert_awaited_once_with(
        per_page=100, include="contacts"
    )


@pytest.mark.asyncio
async def test_get_client_tool():
    from invoiceninja_mcp import server

    fake_client = AsyncMock()
    fake_client.get_client = AsyncMock(
        return_value={
            "data": {
                "id": "QbY6xop9dz",
                "name": "Faction Events",
                "balance": 10,
                "contacts": [
                    {
                        "first_name": "Jana",
                        "last_name": "Muradova",
                        "email": "finance@factionevents.nl",
                        "send_email": True,
                    }
                ],
            }
        }
    )

    with (
        patch.object(server, "client", fake_client),
        patch.object(server, "money", AsyncMock(side_effect=lambda a, c=None: f"€{a}")),
    ):
        result = await server.get_client.fn("QbY6xop9dz")

    assert "Faction Events" in result
    assert "finance@factionevents.nl" in result
    assert "Jana Muradova" in result
    fake_client.get_client.assert_awaited_once_with(
        "QbY6xop9dz", include="contacts"
    )
