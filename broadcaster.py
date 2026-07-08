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

MESSAGE = """🔥 LAZARUS SECURITY TESTING

💳 Payment: QRIS | USDT | BTC | ETH | TRON
✉️ Order: @MhZerus | @babynocryy

✅ WHY CHOOSE US?
• 15+ target DOWN guaranteed every month
• 52 vectors origin discovery
• WAF bypass (Cloudflare etc)
• Full report harian realtime

📦 PAKET

[ HARIAN ] Rp 500.000
Cocok buat testing, 1 target, full report

[ BULANAN ] Rp 9.000.000
Unlimited target, prioritas 24/7

[ RETAINER ]
1 Bulan : Rp 9.000.000
3 Bulan : Rp 25.000.000
6 Bulan : Rp 45.000.000
1 Tahun : Rp 80.000.000

🎯 LAYANAN
Deindex Google | DDoS | Takedown
Brute Force | Exploit | L7 & L4

📌 Cara Order: Kirim Target → Tes Gratis → Bayar → GAS

🔗 Channel: @LazarusDdos
📞 Contact: @MhZerus"""

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
