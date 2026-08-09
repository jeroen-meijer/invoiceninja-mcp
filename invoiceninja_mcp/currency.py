import json
from typing import Optional

from .client import InvoiceNinjaClient

FALLBACK_CURRENCIES: dict[str, dict[str, str]] = {
    "1": {"code": "USD", "symbol": "$"},
    "2": {"code": "GBP", "symbol": "£"},
    "3": {"code": "EUR", "symbol": "€"},
}


def format_amount_with_currency(amount: float, currency: dict[str, str]) -> str:
    symbol = currency.get("symbol")
    code = currency.get("code", "EUR")

    if symbol:
        return f"{symbol}{amount:.2f}"

    return f"{amount:.2f} {code}"


class CurrencyFormatter:
    def __init__(self, client: InvoiceNinjaClient):
        self._client = client
        self._currencies_by_id: dict[str, dict[str, str]] | None = None
        self._default_currency_id: Optional[str] = None

    async def _ensure_loaded(self) -> None:
        if self._currencies_by_id is None:
            static = await self._client.get("statics")
            data = static.get("data", static)
            currencies = data.get("currencies", []) if isinstance(data, dict) else []
            self._currencies_by_id = {
                str(currency["id"]): currency for currency in currencies
            }
            for currency_id, fallback in FALLBACK_CURRENCIES.items():
                self._currencies_by_id.setdefault(currency_id, fallback)

        if self._default_currency_id is None:
            companies = await self._client.get("companies")
            company_list = companies.get("data") or []
            if company_list:
                settings = company_list[0].get("settings")
                if isinstance(settings, str):
                    settings = json.loads(settings)
                if isinstance(settings, dict) and settings.get("currency_id"):
                    self._default_currency_id = str(settings["currency_id"])

            if self._default_currency_id is None:
                self._default_currency_id = "3"

    def _currency_for(self, currency_id: Optional[str]) -> dict[str, str]:
        assert self._currencies_by_id is not None
        assert self._default_currency_id is not None

        resolved_id = str(currency_id or self._default_currency_id)
        return self._currencies_by_id.get(
            resolved_id,
            FALLBACK_CURRENCIES.get(resolved_id, {"code": "EUR", "symbol": "€"}),
        )

    async def format_amount(
        self, amount: float, currency_id: Optional[str] = None
    ) -> str:
        await self._ensure_loaded()
        return format_amount_with_currency(amount, self._currency_for(currency_id))
