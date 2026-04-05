from __future__ import annotations

from typing import Any

import aiohttp

from app.config import settings


class MarketFetcher:
    BASE_URL = "https://api.skinport.com/v1"

    async def _get_json(self, session: aiohttp.ClientSession, url: str, params: dict[str, Any]) -> Any:
        headers = {
            "Accept-Encoding": "br",
        }
        async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_many(self, market_names: list[str], source: str = "skinport") -> list[dict[str, Any]]:
        """
        Returns one normalized record per requested market name.

        listing_price -> Skinport min_price
        baseline_price -> Skinport last_7_days.avg
        volume -> Skinport last_7_days.volume
        """
        market_names = list(dict.fromkeys(market_names))
        if not market_names:
            return []

        params_items = {
            "app_id": 730,
            "currency": settings.skinport_currency,
            "tradable": 0,
        }

        params_history = {
            "app_id": 730,
            "currency": settings.skinport_currency,
            "market_hash_name": ",".join(market_names),
        }

        async with aiohttp.ClientSession() as session:
            items_data = await self._get_json(
                session,
                f"{self.BASE_URL}/items",
                params_items,
            )
            history_data = await self._get_json(
                session,
                f"{self.BASE_URL}/sales/history",
                params_history,
            )

        items_lookup = {
            item["market_hash_name"]: item
            for item in items_data
            if item.get("market_hash_name") in market_names
        }

        history_lookup = {
            item["market_hash_name"]: item
            for item in history_data
            if item.get("market_hash_name") in market_names
        }

        results: list[dict[str, Any]] = []

        for market_name in market_names:
            item_row = items_lookup.get(market_name)
            history_row = history_lookup.get(market_name)

            if not item_row or not history_row:
                continue

            min_price = item_row.get("min_price")
            last_7_days = history_row.get("last_7_days") or {}
            baseline_price = last_7_days.get("avg")
            volume = last_7_days.get("volume")

            if min_price is None or baseline_price is None:
                continue

            results.append(
                {
                    "market_name": market_name,
                    "listing_price": float(min_price),
                    "baseline_price": float(baseline_price),
                    "volume": int(volume) if volume is not None else None,
                    "source": source,
                }
            )

        return results
