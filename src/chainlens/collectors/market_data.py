"""Market-data (OHLCV) collector from public APIs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from chainlens.collectors.base import AsyncCollectorBase
from chainlens.models import PriceCandle, PriceSeries


class MarketDataClient(AsyncCollectorBase):
    """Fetch OHLCV price data from Coingecko or CoinMarketCap."""

    def __init__(self, provider: str = "coingecko", api_key: str = "") -> None:
        super().__init__()
        self.provider = provider
        self.api_key = api_key

    async def get_ohlcv(
        self,
        symbol: str,
        vs_currency: str = "usd",
        days: int = 90,
    ) -> PriceSeries:
        if self.provider == "coingecko":
            return await self._coingecko_ohlcv(symbol, vs_currency, days)
        msg = f"Unsupported provider: {self.provider}"
        raise ValueError(msg)

    async def _coingecko_ohlcv(
        self, coin_id: str, vs_currency: str, days: int
    ) -> PriceSeries:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
        params: dict[str, Any] = {
            "vs_currency": vs_currency,
            "days": str(days),
        }
        if self.api_key:
            params["x_cg_pro_api_key"] = self.api_key

        resp = await self._request("GET", url, params=params)
        raw: list[list] = resp.json()

        candles: list[PriceCandle] = []
        for entry in raw:
            ts = datetime.fromtimestamp(entry[0] / 1000, tz=UTC)
            candles.append(
                PriceCandle(
                    timestamp=ts,
                    open=entry[1],
                    high=entry[2],
                    low=entry[3],
                    close=entry[4],
                    volume=0.0,  # Coingecko OHLC endpoint doesn't return volume
                )
            )

        now = datetime.now(UTC)
        return PriceSeries(
            symbol=coin_id,
            source=f"coingecko/{vs_currency}",
            interval=f"{days}d",
            candles=candles,
            retrieved_at=now,
            sample_size=len(candles),
        )

    async def search_token(self, query: str) -> list[dict[str, str]]:
        if self.provider == "coingecko":
            url = "https://api.coingecko.com/api/v3/search"
            params = {"query": query}
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            resp = await self._request("GET", url, params=params)
            data: dict[str, Any] = resp.json()
            return [
                {"id": c["id"], "symbol": c["symbol"], "name": c["name"]}
                for c in data.get("coins", [])
            ]
        return []

    async def get_current_price(self, coin_id: str) -> float:
        if self.provider == "coingecko":
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": coin_id, "vs_currencies": "usd"}
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            resp = await self._request("GET", url, params=params)
            data: dict[str, Any] = resp.json()
            return data.get(coin_id, {}).get("usd", 0.0)
        return 0.0
