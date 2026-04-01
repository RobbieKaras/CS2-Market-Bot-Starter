from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    database_path: str = os.getenv("DATABASE_PATH", "cs2_market.db")
    scan_interval_seconds: int = int(os.getenv("SCAN_INTERVAL_SECONDS", "300"))
    min_profit_usd: float = float(os.getenv("MIN_PROFIT_USD", "0.50"))
    min_discount_percent: float = float(os.getenv("MIN_DISCOUNT_PERCENT", "12"))
    alert_cooldown_minutes: int = int(os.getenv("ALERT_COOLDOWN_MINUTES", "60"))


settings = Settings()
