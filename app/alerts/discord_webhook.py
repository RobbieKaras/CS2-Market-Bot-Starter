from __future__ import annotations

import aiohttp

from app.config import settings


async def send_webhook_message(content: str) -> bool:
    if not settings.discord_webhook_url:
        print("No Discord webhook configured. Printing alert instead:\n")
        print(content)
        return True

    payload = {"content": content}

    async with aiohttp.ClientSession() as session:
        async with session.post(settings.discord_webhook_url, json=payload) as response:
            return 200 <= response.status < 300
