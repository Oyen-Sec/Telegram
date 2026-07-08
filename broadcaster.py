#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatWriteForbidden, UserChannelsTooMuch
from utils import log, jitter, load_sources
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

MESSAGE = """═══ LAZARUS DDOS SERVICE ═══

✅ SPECIAL SECURITY TESTING
💳 QRIS / USDT / BTC / ETH / TRON
✉️ @MhZerus | @babynocryy

━━━ PAKET ━━━

[ HARIAN ] Rp 500.000
1 target, full report

[ BULANAN ] Rp 9.000.000
Unlimited target, 15 target DOWN guaranteed

[ RETAINER ]
1 BLN : Rp 9.000.000
3 BLN : Rp 25.000.000
6 BLN : Rp 45.000.000
1 THN : Rp 80.000.000

━━━ LAYANAN ━━━
• Deindex Google
• DDoS Web Slot/Judi
• Takedown Server
• WAF Bypass
• Origin Discovery

━━━ CARA ORDER ━━━
Kirim Target → Tes Gratis → Bayar → GAS

⚠️ Refund: < 10 target bisa diatur ulang

🔗 @LazarusDdos | @mhZerus"""

running = True

async def send_to_group(app, group, index, total):
    global running
    if not running:
        return False
    try:
        await app.send_message(group, MESSAGE)
        log("SUCCESS", f"[{index}/{total}] Sent to {group}")
        return True
    except FloodWait as e:
        log("FLOOD", f"Flood wait {e.value}s on {group}")
        await asyncio.sleep(e.value)
        return False
    except ChatWriteForbidden:
        log("SKIP", f"[{index}/{total}] Cannot write in {group} (no permission)")
        return False
    except UserChannelsTooMuch:
        log("ERROR", "Too many channels/groups joined.")
        return False
    except Exception as e:
        err = str(e)[:100]
        log("FAIL", f"[{index}/{total}] {group}: {err}")
        return False

async def main():
    global running

    sources = load_sources(config.SOURCES_FILE)
    if not sources:
        log("ERROR", "No source groups found in sources.txt")
        sys.exit(1)

    log("INFO", f"Loaded {len(sources)} target groups")
    log("INFO", "Starting broadcast...")

    try:
        app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
        await app.start()
        log("INFO", "Session started")
    except Exception as e:
        log("ERROR", f"Failed to start: {e}")
        return

    total = len(sources)
    index = 0
    while running:
        group = sources[index % total]
        await send_to_group(app, group, (index % total) + 1, total)
        index += 1
        if running:
            log("WAIT", "Waiting 10s before next broadcast...")
            await asyncio.sleep(10)

    await app.stop()
    log("INFO", "Broadcaster stopped")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    def silent_exc_handler(loop, context):
        msg = str(context.get("exception", ""))
        if "Peer id invalid" in msg or "ID not found" in msg or "handle_updates" in str(context.get("message", "")):
            return
        loop.default_exception_handler(context)
    loop.set_exception_handler(silent_exc_handler)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
