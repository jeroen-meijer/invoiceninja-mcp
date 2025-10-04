import pytest


@pytest.mark.asyncio
async def test_list_clients(client):
    result = await client.list_clients(per_page=5)
    assert "data" in result
    assert isinstance(result["data"], list)


@pytest.mark.asyncio
async def test_list_invoices(client):
    result = await client.list_invoices(per_page=5)
    assert "data" in result
    assert isinstance(result["data"], list)


@pytest.mark.asyncio
async def test_list_expenses(client):
    result = await client.list_expenses(per_page=5)
    assert "data" in result
    assert isinstance(result["data"], list)
