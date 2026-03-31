from app.analyzers.arbitrage import (
    calculate_baseline,
    calculate_discount_percent,
    estimate_profit_after_fee,
)


def test_calculate_baseline() -> None:
    assert calculate_baseline([1.0, 2.0, 3.0]) == 2.0


def test_discount_percent() -> None:
    assert calculate_discount_percent(8.0, 10.0) == 20.0


def test_estimate_profit_after_fee() -> None:
    assert estimate_profit_after_fee(8.0, 10.0, fee_rate=0.10) == 1.0
