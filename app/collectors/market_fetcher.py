from __future__ import annotations

import asyncio
import random
from typing import Any


class MarketFetcher:
    """
    Starter fetcher.

    Right now this simulates market data so you can build the rest of the app.
    Later, replace this with real site/API integrations.
    """

    async def fetch_item(self, market_name: str, source: str = "steam") -> dict[str, Any]:
        await asyncio.sleep(0.05)

        base_prices = {
            "AK-47 | Slate (Field-Tested)": 4.50,
            "M4A4 | Magnesium (Field-Tested)": 0.85,
            "USP-S | Ticket to Hell (Field-Tested)": 1.70,
        }

        base = base_prices.get(market_name, 2.00)
        simulated_price = round(max(0.03, random.uniform(base * 0.75, base * 1.15)), 2)
        simulated_volume = random.randint(20, 250)

        return {
            "market_name": market_name,
            "listing_price": simulated_price,
            "volume": simulated_volume,
            "source": source,
        }

    async def fetch_many(self, market_names: list[str], source: str = "steam") -> list[dict[str, Any]]:
        tasks = [self.fetch_item(name, source=source) for name in market_names]
        return await asyncio.gather(*tasks)
