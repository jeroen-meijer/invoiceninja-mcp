import pytest
import httpx
from invoiceninja_mcp.config import settings


@pytest.mark.asyncio
async def test_connection_with_debug_info(client):
    base_url = settings.api_url.rstrip("/")
    headers = {
        "X-API-Token": settings.api_key,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = f"{base_url}/clients?per_page=5"

    async with httpx.AsyncClient(timeout=30) as http_client:
        response = await http_client.get(url, headers=headers)
        assert response.status_code == 200
        assert "data" in response.json()


@pytest.mark.asyncio
async def test_api_url_format():
    assert settings.api_url.startswith("http")
    assert len(settings.api_key) > 20
