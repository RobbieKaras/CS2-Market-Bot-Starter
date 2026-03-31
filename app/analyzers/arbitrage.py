from __future__ import annotations

from statistics import mean


def calculate_baseline(recent_prices: list[float]) -> float | None:
    if len(recent_prices) < 3:
        return None
    return round(mean(recent_prices), 2)


def calculate_discount_percent(listing_price: float, baseline_price: float) -> float:
    if baseline_price <= 0:
        return 0.0
    return round(((baseline_price - listing_price) / baseline_price) * 100, 2)


def estimate_profit_after_fee(listing_price: float, baseline_price: float, fee_rate: float = 0.15) -> float:
    estimated_sale_after_fee = baseline_price * (1 - fee_rate)
    return round(estimated_sale_after_fee - listing_price, 2)


def score_opportunity(discount_percent: float, estimated_profit: float, volume: int | None) -> float:
    liquidity_bonus = min((volume or 0) / 10, 20)
    score = (discount_percent * 0.5) + (estimated_profit * 25) + liquidity_bonus
    return round(score, 2)
