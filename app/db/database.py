from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import settings


def get_connection() -> sqlite3.Connection:
    db_path = Path(settings.database_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_name TEXT NOT NULL UNIQUE,
            weapon TEXT,
            skin_name TEXT,
            wear TEXT,
            rarity TEXT,
            collection_name TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            listing_price REAL NOT NULL,
            volume INTEGER,
            captured_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            source TEXT NOT NULL,
            listing_price REAL NOT NULL,
            baseline_price REAL NOT NULL,
            estimated_profit REAL NOT NULL,
            discount_percent REAL NOT NULL,
            score REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts_sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER NOT NULL,
            sent_at TEXT NOT NULL,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        )
        """
    )

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_snapshots_item_time ON price_snapshots(item_id, captured_at)"
    )

    conn.commit()
    conn.close()
