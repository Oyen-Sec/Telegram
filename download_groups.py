#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import re
import os
import sys
import logging
from urllib.request import urlopen, Request
from utils import log
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

SOURCES_FILE = config.SOURCES_FILE

RAW_URLS = [
    "https://raw.githubusercontent.com/itgoyo/TelegramGroup/master/README.md",
    "https://raw.githubusercontent.com/handsomesyx2/TelegramChannel/main/README.md",
    "https://raw.githubusercontent.com/aha-woo/telegram_channel_collect/main/README.md",
    "https://raw.githubusercontent.com/jackhawks/rectg/main/README.md",
    "https://raw.githubusercontent.com/henry-bai3006/TGgroup/main/README.md",
    "https://raw.githubusercontent.com/CorrieOnly/telegram-list/master/README.md",
    "https://raw.githubusercontent.com/tghub/telegram-list/master/README.md",
    "https://raw.githubusercontent.com/Gavinchen92/telegram-groups/main/README.md",
    "https://raw.githubusercontent.com/ds19991999/TgList/master/doc/Telegram%E7%BE%A4%E7%BB%84%E5%AF%BC%E8%88%AA.md",
    "https://raw.githubusercontent.com/hendisantika/List-All-Programming-Telegram-Group/master/README.md",
    "https://raw.githubusercontent.com/lawrencegs/grup-telegram-developer-id/master/README.md",
    "https://raw.githubusercontent.com/aanfaisal/ListTelegram/master/README.md",
    "https://raw.githubusercontent.com/ItIsMeCall911/Awesome-Telegram-OSINT/main/README.md",
    "https://raw.githubusercontent.com/palark/awesome-devops-telegram/master/README.md",
    "https://raw.githubusercontent.com/learn-anything/telegram-groups/master/readme.md",
    "https://raw.githubusercontent.com/telegram-list/telegram-list/master/README.md",
    "https://raw.githubusercontent.com/telegramchannels/telegramchannels/master/README.md",
    "https://raw.githubusercontent.com/telegram-group-list/telegram-group-list/master/README.md",
    "https://raw.githubusercontent.com/telegram-groups/telegram-groups/master/README.md",
    "https://raw.githubusercontent.com/telegram-groups-collection/telegram-groups-collection/master/README.md",
    "https://raw.githubusercontent.com/telegramlist/telegramlist/master/README.md",
    "https://raw.githubusercontent.com/telegramchannelslist/telegramchannelslist/master/README.md",
    "https://raw.githubusercontent.com/tg-groups/tg-groups/master/README.md",
    "https://raw.githubusercontent.com/telegram-groups-list/telegram-groups-list/master/README.md",
    "https://raw.githubusercontent.com/telegram-crypto/telegram-crypto/master/README.md",
]

def extract_usernames(text):
    usernames = set()
    patterns = [
        r't\.me\/([a-zA-Z0-9_]{5,})',
        r'@([a-zA-Z0-9_]{5,})',
    ]
    for p in patterns:
        for m in re.finditer(p, text):
            name = m.group(1)
            if name.lower() not in ('joinchat', 'addlist', 'bot', 'telegraph', 'socks'):
                usernames.add(name.lower())
    return usernames

def fetch_text(url):
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        log("ERROR", f"Failed to fetch {url}: {str(e)[:80]}")
        return ""

async def main():
    log("INFO", "Downloading Telegram group lists from GitHub...")

    existing = set()
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    name = line.replace("@", "").replace("https://t.me/", "").strip().lower()
                    if name:
                        existing.add(name)

    all_new = set()
    for url in RAW_URLS:
        text = fetch_text(url)
        if text:
            usernames = extract_usernames(text)
            new = {u for u in usernames if u not in existing}
            all_new.update(new)
            log("SUCCESS", f"{url.split('/')[4]}: found {len(usernames)} usernames, {len(new)} new")

    if not all_new:
        log("INFO", "No new groups found")
        return

    with open(SOURCES_FILE, "a", encoding="utf-8") as f:
        for name in sorted(all_new):
            f.write(f"@{name}\n")

    log("SUCCESS", f"Added {len(all_new)} new groups to sources.txt")
    log("INFO", f"Total: {len(existing)} + {len(all_new)} = {len(existing) + len(all_new)} groups")

if __name__ == "__main__":
    asyncio.run(main())
