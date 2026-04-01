from __future__ import annotations

import asyncio

from app.alerts.discord_webhook import send_webhook_message
from app.alerts.formatter import format_discord_alert
from app.analyzers.arbitrage import (
    calculate_baseline,
    calculate_discount_percent,
    estimate_profit_after_fee,
    score_opportunity,
)
from app.collectors.market_fetcher import MarketFetcher
from app.collectors.normalizer import normalize_market_record
from app.config import settings
from app.db.database import init_db
from app.db.queries import (
    get_all_items,
    get_recent_prices,
    get_unsent_opportunities,
    has_recent_alert_for_item,
    insert_opportunity,
    insert_price_snapshot,
    mark_alert_sent,
    seed_items_from_json,
)
from app.logger import get_logger

logger = get_logger(__name__)


async def run_scan_cycle() -> None:
    items = get_all_items()
    if not items:
        logger.warning("No items found. Seed your DB first.")
        return

    fetcher = MarketFetcher()
    market_names = [item["market_name"] for item in items]
    raw_results = await fetcher.fetch_many(market_names, source="steam")

    item_lookup = {item["market_name"]: item for item in items}

    for raw in raw_results:
        normalized = normalize_market_record(raw, source=raw["source"])
        item = item_lookup[normalized["market_name"]]

        insert_price_snapshot(
            item_id=item["id"],
            source=normalized["source"],
            listing_price=normalized["listing_price"],
            volume=normalized["volume"],
        )

        recent_prices = get_recent_prices(item_id=item["id"], source=normalized["source"], limit=20)
        baseline = calculate_baseline(recent_prices)
        if baseline is None:
            logger.info("Skipping %s until more history is available.", normalized["market_name"])
            continue

        discount_percent = calculate_discount_percent(normalized["listing_price"], baseline)
        estimated_profit = estimate_profit_after_fee(normalized["listing_price"], baseline)
        score = score_opportunity(discount_percent, estimated_profit, normalized["volume"])

        if (
            estimated_profit >= settings.min_profit_usd
            and discount_percent >= settings.min_discount_percent
        ):
            if has_recent_alert_for_item(
                item_id=item["id"],
                source=normalized["source"],
                cooldown_minutes=settings.alert_cooldown_minutes,
            ):
                logger.info(
                    "Skipping duplicate alert for %s because it is still in cooldown.",
                    normalized["market_name"],
                )
                continue

            insert_opportunity(
                item_id=item["id"],
                source=normalized["source"],
                listing_price=normalized["listing_price"],
                baseline_price=baseline,
                estimated_profit=estimated_profit,
                discount_percent=discount_percent,
                score=score,
            )
            logger.info("Opportunity found for %s", normalized["market_name"])

    unsent = get_unsent_opportunities()
    for opportunity in unsent:
        message = format_discord_alert(opportunity)
        sent = await send_webhook_message(message)
        if sent:
            mark_alert_sent(opportunity["opportunity_id"])
            logger.info("Alert sent for opportunity %s", opportunity["opportunity_id"])


async def main() -> None:
    init_db()
    seed_items_from_json("data/items.json")

    logger.info("Starting CS2 market bot...")
    while True:
        try:
            await run_scan_cycle()
        except Exception as exc:
            logger.exception("Scan cycle failed: %s", exc)

        logger.info("Sleeping for %s seconds...", settings.scan_interval_seconds)
        await asyncio.sleep(settings.scan_interval_seconds)


if __name__ == "__main__":
    asyncio.run(main())
