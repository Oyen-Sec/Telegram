#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, UsernameNotOccupied, PeerIdInvalid
from utils import log, load_sources
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)

async def main():
    sources = load_sources(sys.argv[1]) if len(sys.argv) > 1 else load_sources(config.SOURCES_FILE)
    if not sources:
        log("ERROR", "No sources file specified")
        sys.exit(1)

    log("INFO", f"Scanning {len(sources)} groups...")

    app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH, no_updates=True)
    await app.start()

    results = []
    for i, username in enumerate(sources):
        try:
            chat = await app.get_chat(username)
            members = chat.members_count if hasattr(chat, 'members_count') else '?'
            title = chat.title if hasattr(chat, 'title') else username
            results.append((members if isinstance(members, int) else 0, username, title))
            log("OK", f"[{i+1}/{len(sources)}] {username} → {members} members")
        except FloodWait as e:
            log("FLOOD", f"Flood wait {e.value}s")
            await asyncio.sleep(e.value)
        except (UsernameNotOccupied, PeerIdInvalid):
            log("DEAD", f"[{i+1}/{len(sources)}] {username} → NOT FOUND")
        except Exception as e:
            log("ERR", f"[{i+1}/{len(sources)}] {username} → {str(e)[:60]}")
        await asyncio.sleep(2)

    results.sort(key=lambda x: x[0], reverse=True)

    print("\n" + "=" * 60)
    print("TOP GROUPS BY MEMBER COUNT")
    print("=" * 60)
    for rank, (count, username, title) in enumerate(results, 1):
        print(f"{rank:2d}. [{count:>6}] {username:30s} {title[:40]}")

    await app.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted")
