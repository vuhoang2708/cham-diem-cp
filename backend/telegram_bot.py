"""
Telegram bot integration for SignalBoard VN alerts.
Sends notifications when score changes significantly.
"""
from __future__ import annotations

import os
import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def send_message(chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
    """Send a Telegram message to a specific chat_id."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping alert")
        return False
    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error("Telegram API error: %s", resp.text)
                return False
            return True
    except Exception as e:
        logger.error("Failed to send Telegram message: %s", e)
        return False


def format_score_alert(symbol: str, old_score: float, new_score: float,
                       score_max: float, quadrant_name: str, adx: float) -> str:
    """Format a score change alert message."""
    direction = "⬆️" if new_score > old_score else "⬇️"
    pct = round(new_score / score_max * 100, 1) if score_max > 0 else 0
    return (
        f"<b>📊 SignalBoard VN — Score Alert</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🏷️ <b>{symbol}</b>  {direction}  {old_score:.2f} → {new_score:.2f} / {score_max:.1f}\n"
        f"📈 Phần trăm điểm: <b>{pct}%</b>\n"
        f"📊 RRG: <b>{quadrant_name}</b>\n"
        f"📉 ADX: <b>{adx:.1f}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>SignalBoard VN — https://cham-diem-cp.vercel.app</i>"
    )


async def broadcast_significant_changes(
    scores: list[dict],
    prev_scores: dict[str, float],
    threshold: float = 0.2,
    chat_ids: Optional[list[str]] = None,
) -> int:
    """
    Broadcast alerts for scores that changed by >= threshold.
    Returns number of alerts sent.
    """
    if not chat_ids:
        return 0

    alerts_sent = 0
    for record in scores:
        symbol = record.get("symbol", "")
        new_score = float(record.get("total_score", 0))
        old_score = prev_scores.get(symbol, new_score)
        change = abs(new_score - old_score)

        if change >= threshold:
            quadrant_map = {1: "TĂNG GIÁ", 2: "SUY YẾU", 3: "GIẢM GIÁ", 4: "TÍCH LŨY"}
            quadrant = record.get("rrg_quadrant", 3)
            try:
                quadrant = int(quadrant)
            except (TypeError, ValueError):
                quadrant = 3
            quadrant_name = quadrant_map.get(quadrant, "N/A")
            adx = float(record.get("adx_value", 0))
            score_max = float(record.get("score_max", 2.5))
            msg = format_score_alert(symbol, old_score, new_score, score_max, quadrant_name, adx)
            for chat_id in chat_ids:
                ok = await send_message(chat_id, msg)
                if ok:
                    alerts_sent += 1

    return alerts_sent


async def handle_webhook(update: dict) -> Optional[str]:
    """
    Handle incoming Telegram bot updates (commands from users).
    Returns reply text or None.
    """
    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "").strip()

    if text.startswith("/start"):
        return (
            "👋 Chào mừng đến với <b>SignalBoard VN</b>!\n\n"
            "Bot này sẽ gửi alert khi điểm cổ phiếu VN30 thay đổi đáng kể.\n\n"
            "📌 Lệnh:\n"
            "  /top — Top 5 cổ phiếu điểm cao nhất\n"
            "  /score VCB — Xem điểm chi tiết một mã\n"
            "  /help — Hướng dẫn\n\n"
            "<i>Powered by SignalBoard VN</i>"
        )
    if text.startswith("/help"):
        return (
            "📖 <b>Hướng dẫn SignalBoard VN Bot</b>\n\n"
            "/top — Xem top 5 cổ phiếu\n"
            "/score [MÃ] — Xem điểm cổ phiếu (vd: /score VCB)\n"
            "/start — Bắt đầu\n\n"
            "<i>Web: https://cham-diem-cp.vercel.app</i>"
        )
    if text.startswith("/score "):
        symbol = text.split(" ", 1)[1].upper().strip()
        return f"🔍 Đang tra cứu <b>{symbol}</b>... (tính năng đang phát triển)"
    if text.startswith("/top"):
        return "📊 Đang lấy top 5... (tính năng đang phát triển)"

    return None
