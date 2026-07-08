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

MESSAGE = """🔥✅SPECIAL SECURITY TESTING SERVICE 🔥✅
💳Payment: QRIS | USDT | BTC | ETH | TRON
✉️Order & Info: @MhZerus ✈️

🔥 LAZARUS GRUP — FULL SERVICE 🔥

▶️PAKET HARIAN (TESTING / HOLD)
👉Rp 500.000 / hari
👉1 target spesifik
🔴 Full report harian
👉Cocok buat testing sebelum ambil paket bulanan

▶️PAKET BULANAN (UNLIMITED TARGET)
👉Rp 9.000.000 / bulan
👉 Target UNLIMITED selama 1 bulan
🔴 Full report harian via grup khusus Telegram
👉 Prioritas serangan 24/7
👉 Dijamin 15 target DOWN dalam sebulan

▶️PAKET RETAINER (LANGGANAN JANGKA PANJANG)
🎚1 Bulan — Rp 9.000.000 (Friend: Rp 7.000.000)
🎚 3 Bulan — Rp 25.000.000 (Friend: Rp 20.000.000)
🎚 6 Bulan — Rp 45.000.000 (Friend: Rp 38.000.000)
🎚 1 Tahun — Rp 80.000.000 (Friend: Rp 70.000.000)

Friend Price khusus client referensi dari pembeli lama ✨

▶️LAYANAN KAMI
🟢Turunkan Index Google (Deindex)
🟢 DDoS Web Judi / Slot / Phising
🟢 Takedown Landing Page & Server
🟢 Brute Force & Exploit
🟢 L7 + L4 Full Arsenal
🟢 WAF Bypass (Cloudflare, etc)
🟢 Origin Discovery (52 Vectors)

▶️WORKFLOW (WAJIB)
🎚Kirim Target → Tes Gratis → Bayar → GAS & HOLD
☄️Report harian dikirim via Telegram

⚠️KETENTUAN REFUND
Full payment di awal bulan (sistem retainer).
Jika dalam 1 bulan mencapai 15 target DOWN → Full payment WAJIB (tidak bisa refund).
Jika di bawah 10 target → Bisa diatur ulang / kompensasi sesuai kesepakatan awal.
Grup khusus dibuat untuk client paket bulanan sebagai tempat report real-time.

📢OFFICIAL CONTACT
💳@MhZerus | @babynocryy
🔈Channel: https://t.me/LazarusDdos
⚠️Proof: https://t.me/mhZerus

TAGS
🟢SEO Services
🟢DDoS Services
🟢Hold Services
🟢Suspend Services
🟢Takedown Services
🟢 Phishing
🟢L7 Attack
🟢L4 Attack
🟢Captcha Bypass
🟢Google Takedown
🟢Deindex Services
🟢Slot Takedown"""

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
