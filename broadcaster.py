#!/usr/bin/env python3
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

MESSAGE = """
\xf0\x9f\x94\xb4\xe2\x9c\x85SPECIAL SECURITY TESTING SERVICE \xf0\x9f\x94\xb4\xe2\x9c\x85
\xf0\x9f\x92\xb3Payment: QRIS | USDT | BTC | ETH | TRON
\xe2\x9c\x89\xef\xb8\x8fOrder & Info: @MhZerus \xe2\x9c\x88\xef\xb8\x8f

\xf0\x9f\x94\xa5 LAZARUS GRUP \xe2\x80\x94 FULL SERVICE \xf0\x9f\x94\xa5

\xe2\x96\xb6\xef\xb8\x8fPAKET HARIAN (TESTING / HOLD)
\xf0\x9f\x91\x89Rp 500.000 / hari
\xf0\x9f\x91\x891 target spesifik
\xf0\x9f\x94\xb4 Full report harian
\xf0\x9f\x91\x89Cocok buat testing sebelum ambil paket bulanan

\xe2\x96\xb6\xef\xb8\x8fPAKET BULANAN (UNLIMITED TARGET)
\xf0\x9f\x91\x89Rp 9.000.000 / bulan
\xf0\x9f\x91\x89 Target UNLIMITED selama 1 bulan
\xf0\x9f\x94\xb4 Full report harian via grup khusus Telegram
\xf0\x9f\x91\x89 Prioritas serangan 24/7
\xf0\x9f\x91\x89 Dijamin 15 target DOWN dalam sebulan

\xe2\x96\xb6\xef\xb8\x8fPAKET RETAINER (LANGGANAN JANGKA PANJANG)
\xf0\x9f\x8e\x9a1 Bulan \xe2\x80\x94 Rp 9.000.000 (Friend: Rp 7.000.000)
\xf0\x9f\x8e\x9a 3 Bulan \xe2\x80\x94 Rp 25.000.000 (Friend: Rp 20.000.000)
\xf0\x9f\x8e\x9a 6 Bulan \xe2\x80\x94 Rp 45.000.000 (Friend: Rp 38.000.000)
\xf0\x9f\x8e\x9a 1 Tahun \xe2\x80\x94 Rp 80.000.000 (Friend: Rp 70.000.000)

Friend Price khusus client referensi dari pembeli lama \xe2\x9c\xa8

\xe2\x96\xb6\xef\xb8\x8fLAYANAN KAMI
\xf0\x9f\x9f\xa2Turunkan Index Google (Deindex)
\xf0\x9f\x9f\xa2 DDoS Web Judi / Slot / Phising
\xf0\x9f\x9f\xa2 Takedown Landing Page & Server
\xf0\x9f\x9f\xa2 Brute Force & Exploit
\xf0\x9f\x9f\xa2 L7 + L4 Full Arsenal
\xf0\x9f\x9f\xa2 WAF Bypass (Cloudflare, etc)
\xf0\x9f\x9f\xa2 Origin Discovery (52 Vectors)

\xe2\x96\xb6\xef\xb8\x8fWORKFLOW (WAJIB)
\xf0\x9f\x8e\x9aKirim Target \xe2\x86\x92 Tes Gratis \xe2\x86\x92 Bayar \xe2\x86\x92 GAS & HOLD
\xe2\x98\x84\xef\xb8\x8fReport harian dikirim via Telegram

\xe2\x9a\xa0\xef\xb8\x8fKETENTUAN REFUND
Full payment di awal bulan (sistem retainer).
Jika dalam 1 bulan mencapai 15 target DOWN \xe2\x86\x92 Full payment WAJIB (tidak bisa refund).
Jika di bawah 10 target \xe2\x86\x92 Bisa diatur ulang / kompensasi sesuai kesepakatan awal.
Grup khusus dibuat untuk client paket bulanan sebagai tempat report real-time.

\xf0\x9f\x93\xa2OFFICIAL CONTACT
\xf0\x9f\x92\xb3@MhZerus | @babynocryy
\xf0\x9f\x94\x88Channel: https://t.me/LazarusDdos
\xe2\x9a\xa0\xef\xb8\x8fProof: https://t.me/mhZerus

TAGS
\xf0\x9f\x9f\xa2SEO Services
\xf0\x9f\x9f\xa2DDoS Services
\xf0\x9f\x9f\xa2Hold Services
\xf0\x9f\x9f\xa2Suspend Services
\xf0\x9f\x9f\xa2Takedown Services
\xf0\x9f\x9f\xa2 Phishing
\xf0\x9f\x9f\xa2L7 Attack
\xf0\x9f\x9f\xa2L4 Attack
\xf0\x9f\x9f\xa2Captcha Bypass
\xf0\x9f\x9f\xa2Google Takedown
\xf0\x9f\x9f\xa2Deindex Services
\xf0\x9f\x9f\xa2Slot Takedown
"""

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
            log("WAIT", "Waiting 60s before next broadcast...")
            await asyncio.sleep(60)

    await app.stop()
    log("INFO", "Broadcaster stopped")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
