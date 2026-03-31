from __future__ import annotations


def format_discord_alert(opportunity: dict) -> str:
    return (
        "🚨 **Underpriced Listing Detected**\n\n"
        f"**Item:** {opportunity['market_name']}\n"
        f"**Source:** {opportunity['source']}\n"
        f"**Current Price:** ${opportunity['listing_price']:.2f}\n"
        f"**Baseline Price:** ${opportunity['baseline_price']:.2f}\n"
        f"**Estimated Profit After Fees:** ${opportunity['estimated_profit']:.2f}\n"
        f"**Discount:** {opportunity['discount_percent']:.2f}%\n"
        f"**Score:** {opportunity['score']:.2f}\n"
        f"**Detected:** {opportunity['created_at']}"
    )
