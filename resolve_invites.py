#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import logging
from pyrogram import Client
from utils import log, load_sources
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

SOURCES_FILE = config.SOURCES_FILE
INVITE_PREFIX = "https://t.me/addlist/"

async def main():
    sources = load_sources(SOURCES_FILE)
    invite_links = [s for s in sources if s.startswith(INVITE_PREFIX)]
    regular = [s for s in sources if not s.startswith(INVITE_PREFIX)]

    if not invite_links:
        log("INFO", "No invite links found in sources.txt")
        return

    log("INFO", f"Found {len(invite_links)} invite links")

    app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
    await app.start()
    log("INFO", "Session started")

    all_group_usernames = set()

    for link in invite_links:
        hash = link.replace(INVITE_PREFIX, "")
        log("INFO", f"Processing invite link: {link}")

        dialogs_before = {}
        async for dialog in app.get_dialogs():
            if dialog.chat.username:
                dialogs_before[dialog.chat.id] = dialog.chat.username

        try:
            chat = await app.join_chat(hash)
            log("SUCCESS", f"Joined folder: {hash}")
        except Exception as e:
            log("ERROR", f"Failed to join folder {hash}: {str(e)[:100]}")
            continue

        await asyncio.sleep(3)

        async for dialog in app.get_dialogs():
            chat_id = dialog.chat.id
            username = dialog.chat.username
            title = dialog.chat.title or "no title"
            if chat_id not in dialogs_before and username:
                if username not in regular and username not in all_group_usernames:
                    all_group_usernames.add(username)
                    log("SUCCESS", f"  Found new group: @{username} ({title})")
                elif username in regular:
                    log("INFO", f"  Already in sources: @{username}")
                elif username in all_group_usernames:
                    log("INFO", f"  Already added from other link: @{username}")

    await app.stop()

    if all_group_usernames:
        new_sources = regular + sorted(all_group_usernames)
        with open(SOURCES_FILE, "w", encoding="utf-8") as f:
            for s in new_sources:
                f.write(s + "\n")
        log("SUCCESS", f"Added {len(all_group_usernames)} new groups to sources.txt")
        log("INFO", f"Total: {len(regular)} + {len(all_group_usernames)} = {len(new_sources)} groups")
    else:
        log("INFO", "No new groups found")

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
