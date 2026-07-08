#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
import time
import urllib.request
import urllib.error
import logging
from collections import deque
from utils import log

logging.getLogger("pyrogram").setLevel(logging.ERROR)

SOURCES_FILE = os.path.join(os.path.dirname(__file__), "sources.txt")
MAX_GROUPS = 100000
DELAY = 2

def fetch_tme_page(username):
    url = f"https://t.me/s/{username}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except Exception:
        return None

def extract_mentions(html):
    found = set()
    for m in re.finditer(r'(?:@|t\.me/s/)([a-zA-Z0-9_]{5,})', html):
        name = m.group(1).lower()
        if name not in ("joinchat", "addlist", "bot", "telegraph", "socks", "telegram",
                        "preview", "username", "spambot", "gif", "stickers", "contact"):
            found.add(name)
    return found

def main():
    if not os.path.exists(SOURCES_FILE):
        log("ERROR", "sources.txt not found")
        return

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        known = {line.strip().replace("@", "").lower() for line in f if line.strip()}

    queue = deque(sorted(known))
    visited = set(known)
    new_found = set()
    processed = 0

    log("INFO", f"Starting snowball crawl with {len(known)} seeds")
    log("INFO", f"Target: {MAX_GROUPS} groups")

    while queue and len(known) + len(new_found) < MAX_GROUPS:
        username = queue.popleft()
        processed += 1

        if processed % 50 == 0:
            total = len(known) + len(new_found)
            log("INFO", f"Processed {processed} | Total: {total} | Queue: {len(queue)} | New: {len(new_found)}")

        html = fetch_tme_page(username)
        if html is None:
            continue

        mentions = extract_mentions(html)
        for name in mentions:
            if name not in visited and name not in new_found:
                new_found.add(name)
                queue.append(name)

        time.sleep(DELAY)

        if processed % 200 == 0:
            if new_found:
                with open(SOURCES_FILE, "a", encoding="utf-8") as f:
                    for n in sorted(new_found):
                        f.write(f"@{n}\n")
                log("SUCCESS", f"Saved {len(new_found)} new groups. Total: {len(known) + len(new_found)}")
                new_found.clear()
                queue = deque(sorted(set(queue)))  # deduplicate

    if new_found:
        with open(SOURCES_FILE, "a", encoding="utf-8") as f:
            for n in sorted(new_found):
                f.write(f"@{n}\n")
        log("SUCCESS", f"Saved {len(new_found)} new groups")

    total = len(known) + len(new_found) + (sum(1 for _ in open(SOURCES_FILE, encoding="utf-8")) - len(known) - len(new_found))
    log("SUCCESS", f"Crawl complete. Total groups: ~{total}")
    log("INFO", f"Processed {processed} pages")

if __name__ == "__main__":
    main()
