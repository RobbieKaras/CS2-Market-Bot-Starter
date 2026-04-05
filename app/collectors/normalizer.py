from __future__ import annotations

from typing import Any


def normalize_market_record(raw: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "source": source,
        "market_name": raw["market_name"],
        "listing_price": float(raw["listing_price"]),
        "baseline_price": float(raw["baseline_price"]),
        "volume": int(raw["volume"]) if raw.get("volume") is not None else None,
    }
