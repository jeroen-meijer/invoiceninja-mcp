import pytest
from unittest.mock import AsyncMock
from invoiceninja_mcp.server import _generate_btw_report


@pytest.fixture
def mock_invoices_q1_2024():
    return {
        "data": [
            {
                "id": "inv1",
                "date": "2024-01-15",
                "amount": 1210.0,
                "total_taxes": 210.0,
            },
            {
                "id": "inv2",
                "date": "2024-02-20",
                "amount": 605.0,
                "total_taxes": 105.0,
            },
            {
                "id": "inv3",
                "date": "2024-03-10",
                "amount": 1815.0,
                "total_taxes": 315.0,
            },
            {
                "id": "inv4",
                "date": "2024-04-05",
                "amount": 1210.0,
                "total_taxes": 210.0,
            },
        ]
    }


@pytest.fixture
def mock_expenses_q1_2024():
    return {
        "data": [
            {
                "id": "exp1",
                "expense_date": "2024-01-10",
                "amount": 100.0,
                "tax_rate1": 21,
            },
            {
                "id": "exp2",
                "expense_date": "2024-02-15",
                "amount": 250.0,
                "tax_rate1": 21,
            },
            {
                "id": "exp3",
                "date": "2024-03-20",
                "amount": 150.0,
                "tax_rate1": 21,
            },
            {
                "id": "exp4",
                "expense_date": "2024-04-01",
                "amount": 200.0,
                "tax_rate1": 21,
            },
        ]
    }


@pytest.fixture
def mock_empty_data():
    return {"data": []}


@pytest.mark.asyncio
async def test_btw_report_q1_2024_with_data(
    mock_invoices_q1_2024, mock_expenses_q1_2024
):
    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices_q1_2024)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses_q1_2024)

    report = await _generate_btw_report(2024, 1, mock_client)

    assert isinstance(report, str)
    assert "BTW Quarterly Report for Q1 2024" in report
    assert "2024-01-01 to 2024-03-31" in report

    assert "€3630.00" in report
    assert "€3000.00" in report
    assert "€630.00" in report

    assert "€500.00" in report
    assert "€105.00" in report

    assert "€525.00" in report


@pytest.mark.asyncio
async def test_btw_report_empty_invoices_expenses(mock_empty_data):
    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_empty_data)
    mock_client.list_expenses = AsyncMock(return_value=mock_empty_data)

    report = await _generate_btw_report(2024, 2, mock_client)

    assert isinstance(report, str)
    assert "BTW Quarterly Report for Q2 2024" in report
    assert "€0.00" in report


@pytest.mark.asyncio
async def test_btw_report_invalid_quarter():
    mock_client = AsyncMock()
    report = await _generate_btw_report(2024, 5, mock_client)
    assert "❌ Quarter must be 1, 2, 3, or 4" in report


@pytest.mark.asyncio
async def test_btw_report_expenses_without_21_percent_tax():
    mock_invoices = {"data": []}
    mock_expenses = {
        "data": [
            {
                "id": "exp1",
                "expense_date": "2024-07-10",
                "amount": 500.0,
                "tax_rate1": 9,
            },
            {
                "id": "exp2",
                "expense_date": "2024-08-15",
                "amount": 300.0,
                "tax_rate1": 0,
            },
        ]
    }

    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses)

    report = await _generate_btw_report(2024, 3, mock_client)

    assert "€800.00" in report
    assert "BTW paid over these expenses | €0.00" in report


@pytest.mark.asyncio
async def test_btw_report_filters_by_quarter_correctly():
    mock_invoices = {
        "data": [
            {
                "id": "inv1",
                "date": "2024-01-15",
                "amount": 1210.0,
                "total_taxes": 210.0,
            },
            {
                "id": "inv2",
                "date": "2024-05-20",
                "amount": 605.0,
                "total_taxes": 105.0,
            },
        ]
    }

    mock_expenses = {
        "data": [
            {
                "id": "exp1",
                "expense_date": "2024-01-10",
                "amount": 100.0,
                "tax_rate1": 21,
            },
            {
                "id": "exp2",
                "expense_date": "2024-06-15",
                "amount": 250.0,
                "tax_rate1": 21,
            },
        ]
    }

    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses)

    report = await _generate_btw_report(2024, 1, mock_client)

    assert "€1210.00" in report
    assert "€210.00" in report
    assert "€100.00" in report
    assert "€21.00" in report


@pytest.mark.asyncio
async def test_btw_report_handles_none_values():
    mock_invoices = {
        "data": [
            {
                "id": "inv1",
                "date": "2024-10-15",
                "amount": None,
                "total_taxes": None,
            },
            {
                "id": "inv2",
                "date": "2024-11-20",
                "amount": 1210.0,
                "total_taxes": 210.0,
            },
        ]
    }

    mock_expenses = {
        "data": [
            {
                "id": "exp1",
                "expense_date": "2024-10-10",
                "amount": None,
                "tax_rate1": 21,
            },
            {
                "id": "exp2",
                "expense_date": "2024-11-15",
                "amount": 100.0,
                "tax_rate1": None,
            },
        ]
    }

    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses)

    report = await _generate_btw_report(2024, 4, mock_client)

    assert isinstance(report, str)
    assert "BTW Quarterly Report for Q4 2024" in report


@pytest.mark.asyncio
async def test_btw_difference_calculation():
    mock_invoices = {
        "data": [
            {
                "id": "inv1",
                "date": "2024-04-15",
                "amount": 1210.0,
                "total_taxes": 210.0,
            },
        ]
    }

    mock_expenses = {
        "data": [
            {
                "id": "exp1",
                "expense_date": "2024-05-10",
                "amount": 100.0,
                "tax_rate1": 21,
            },
        ]
    }

    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses)

    report = await _generate_btw_report(2024, 2, mock_client)

    assert "Total BTW difference | €189.00" in report


@pytest.mark.asyncio
async def test_btw_report_expense_with_fallback_date_field():
    mock_invoices = {"data": []}
    mock_expenses = {
        "data": [
            {
                "id": "exp1",
                "date": "2024-07-10",
                "amount": 100.0,
                "tax_rate1": 21,
            },
        ]
    }

    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses)

    report = await _generate_btw_report(2024, 3, mock_client)

    assert "€100.00" in report
    assert "€21.00" in report


@pytest.mark.asyncio
async def test_btw_report_international_invoices_zero_tax():
    mock_invoices = {
        "data": [
            {
                "id": "inv1",
                "date": "2024-01-15",
                "amount": 1000.0,
                "total_taxes": 210.0,
            },
            {
                "id": "inv2",
                "date": "2024-02-20",
                "amount": 2000.0,
                "total_taxes": 0.0,
            },
            {
                "id": "inv3",
                "date": "2024-03-10",
                "amount": 1500.0,
                "total_taxes": 0,
            },
        ]
    }

    mock_expenses = {"data": []}

    mock_client = AsyncMock()
    mock_client.list_invoices = AsyncMock(return_value=mock_invoices)
    mock_client.list_expenses = AsyncMock(return_value=mock_expenses)

    report = await _generate_btw_report(2024, 1, mock_client)

    assert "€4500.00" in report
    assert "€4290.00" in report
    assert "Total BTW amount over invoices | €210.00" in report
    assert "Total BTW difference | €210.00" in report
