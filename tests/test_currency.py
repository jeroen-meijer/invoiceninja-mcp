from invoiceninja_mcp.currency import format_amount_with_currency, FALLBACK_CURRENCIES


def test_format_amount_with_eur_symbol():
    assert format_amount_with_currency(327.0, FALLBACK_CURRENCIES["3"]) == "€327.00"


def test_format_amount_with_usd_symbol():
    assert format_amount_with_currency(100.0, FALLBACK_CURRENCIES["1"]) == "$100.00"


def test_format_amount_without_symbol_uses_code():
    currency = {"code": "CHF"}
    assert format_amount_with_currency(50.5, currency) == "50.50 CHF"
