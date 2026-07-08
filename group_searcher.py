#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait
from utils import log, async_sleep
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

SOURCES_FILE = config.SOURCES_FILE

KEYWORDS = [
    "webshell", "cpanel", "shell", "seo", "ddos", "judi", "slot",
    "hacking", "indonesia", "hack", "defacer", "root", "exploit",
    "spam", "sms", "call", "tools", "cracking", "phising", "scam",
    "market", "shop", "store", "seller", "buyer", "jual", "beli",
    "sewa", "vps", "rdp", "smtp", "mailer", "panel", "botnet",
    "malware", "virus", "trojan", "backdoor", "bypass", "inject",
    "payload", "shellback", "obfuscate", "encode", "decode",
    "darkweb", "darknet", "carding", "bank", "log", "card",
    "dumps", "fullz", "ccn", "bitcoin", "crypto", "bnb", "eth",
    "free fire", "ff", "mlbb", "mobile legend", "pubg", "server",
    "vpn", "proxy", "config", "openvpn", "wireguard", "panel",
    "streaming", "film", "movie", "drama", "anime", "nonton",
    "bokep", "viral", "hot", "18+", "dewasa", "colmek",
    "promo", "diskon", "gratis", "free", "loker", "kerja",
    "lowongan", "bisnis", "money", "income", "profit",
]

running = True

async def main():
    global running

    app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
    await app.start()
    log("INFO", "Session started")

    existing = set()
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().replace("@", "").lower()
                if line:
                    existing.add(line)

    all_new = set()

    for kw in KEYWORDS:
        if not running:
            break
        log("INFO", f"Searching: '{kw}'...")
        try:
            count = 0
            async for msg in app.search_global(kw, limit=50):
                chat = msg.chat
                if chat and chat.username:
                    u = chat.username.lower()
                    if u not in existing and u not in all_new:
                        all_new.add(u)
                        count += 1
            log("SUCCESS", f"  '{kw}': found {count} new groups")
            await async_sleep(3, 6)
        except FloodWait as e:
            log("FLOOD", f"Flood wait {e.value}s")
            await asyncio.sleep(e.value)
        except Exception as e:
            log("ERROR", f"  '{kw}': {str(e)[:80]}")
            await asyncio.sleep(5)

    if all_new:
        with open(SOURCES_FILE, "a", encoding="utf-8") as f:
            for u in sorted(all_new):
                f.write(f"@{u}\n")
        total_new = len(all_new)
        total_all = len(existing) + total_new
        log("SUCCESS", f"Added {total_new} new groups from search")
        log("INFO", f"Total: {total_all} groups")
    else:
        log("INFO", "No new groups found via search")

    await app.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
