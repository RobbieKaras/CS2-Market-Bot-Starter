from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.db.database import get_connection


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_items_from_json(json_path: str) -> None:
    path = Path(json_path)
    items = json.loads(path.read_text(encoding="utf-8"))

    conn = get_connection()
    cur = conn.cursor()

    for item in items:
        cur.execute(
            """
            INSERT OR IGNORE INTO items (
                market_name, weapon, skin_name, wear, rarity, collection_name
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item["market_name"],
                item.get("weapon"),
                item.get("skin_name"),
                item.get("wear"),
                item.get("rarity"),
                item.get("collection"),
            ),
        )

    conn.commit()
    conn.close()


def get_all_items() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM items ORDER BY market_name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_price_snapshot(item_id: int, source: str, listing_price: float, volume: int | None) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO price_snapshots (item_id, source, listing_price, volume, captured_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (item_id, source, listing_price, volume, utc_now_iso()),
    )
    conn.commit()
    conn.close()


def get_recent_prices(item_id: int, source: str, limit: int = 20) -> list[float]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT listing_price
        FROM price_snapshots
        WHERE item_id = ? AND source = ?
        ORDER BY captured_at DESC
        LIMIT ?
        """,
        (item_id, source, limit),
    ).fetchall()
    conn.close()
    return [float(row["listing_price"]) for row in rows]


def insert_opportunity(
    item_id: int,
    source: str,
    listing_price: float,
    baseline_price: float,
    estimated_profit: float,
    discount_percent: float,
    score: float,
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO opportunities (
            item_id, source, listing_price, baseline_price,
            estimated_profit, discount_percent, score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item_id,
            source,
            listing_price,
            baseline_price,
            estimated_profit,
            discount_percent,
            score,
            utc_now_iso(),
        ),
    )
    opportunity_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(opportunity_id)


def has_recent_alert_for_item(item_id: int, source: str, cooldown_minutes: int = 60) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)).isoformat()

    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        """
        SELECT 1
        FROM opportunities o
        JOIN alerts_sent a ON a.opportunity_id = o.id
        WHERE o.item_id = ?
          AND o.source = ?
          AND a.sent_at >= ?
        LIMIT 1
        """,
        (item_id, source, cutoff),
    ).fetchone()
    conn.close()
    return row is not None


def get_unsent_opportunities() -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT
            o.id AS opportunity_id,
            i.market_name,
            o.source,
            o.listing_price,
            o.baseline_price,
            o.estimated_profit,
            o.discount_percent,
            o.score,
            o.created_at
        FROM opportunities o
        JOIN items i ON i.id = o.item_id
        LEFT JOIN alerts_sent a ON a.opportunity_id = o.id
        WHERE a.id IS NULL
        ORDER BY o.score DESC, o.created_at DESC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_alert_sent(opportunity_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO alerts_sent (opportunity_id, sent_at) VALUES (?, ?)",
        (opportunity_id, utc_now_iso()),
    )
    conn.commit()
    conn.close()
