#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatWriteForbidden, UserChannelsTooMuch
from utils import log, load_sources
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

running = True

async def main():
    global running

    if len(sys.argv) < 4:
        print("Usage: python forwarder.py <source_chat> <message_id> <delay_seconds>")
        print("Example: python forwarder.py @MhZerus 123 10")
        sys.exit(1)

    source_chat = sys.argv[1]
    message_id = int(sys.argv[2])
    delay = int(sys.argv[3])

    sources = load_sources(config.SOURCES_FILE)
    if not sources:
        log("ERROR", "No target groups in sources.txt")
        sys.exit(1)

    log("INFO", f"Source: {source_chat}, Message ID: {message_id}")
    log("INFO", f"Targets: {len(sources)} groups, Delay: {delay}s")

    try:
        app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
        await app.start()
        log("INFO", "Session started")
    except Exception as e:
        log("ERROR", f"Failed to start: {e}")
        return

    index = 0
    total = len(sources)
    while running:
        group = sources[index % total]
        try:
            await app.forward_messages(group, source_chat, [message_id])
            log("SUCCESS", f"[{(index % total) + 1}/{total}] Forwarded to {group}")
        except FloodWait as e:
            log("FLOOD", f"Flood wait {e.value}s")
            await asyncio.sleep(e.value)
            continue
        except ChatWriteForbidden:
            log("SKIP", f"[{(index % total) + 1}/{total}] Cannot write in {group}")
        except UserChannelsTooMuch:
            log("ERROR", "Too many groups joined")
            break
        except Exception as e:
            log("FAIL", f"[{(index % total) + 1}/{total}] {group}: {str(e)[:80]}")

        index += 1
        if running:
            await asyncio.sleep(delay)

    await app.stop()
    log("INFO", "Forwarder stopped")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
