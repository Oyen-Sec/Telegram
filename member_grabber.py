#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import json
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, UsernameNotOccupied, PeerIdInvalid, UserChannelsTooMuch, ChatWriteForbidden, UserNotMutualContact
from utils import log, load_sources
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)

SAVE_FILE = os.path.join(os.path.dirname(__file__), "members.json")

def load_members():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            return set(json.load(f))
    return set()

def save_members(members):
    with open(SAVE_FILE, "w") as f:
        json.dump(list(members), f)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python member_grabber.py <sources_file> [delay_between_groups]")
        sys.exit(1)

    sources = load_sources(sys.argv[1])
    delay = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    target = config.TARGET_GROUP

    log("INFO", f"Target group: {target}")
    log("INFO", f"Source groups: {len(sources)}, Delay: {delay}s")

    saved_members = load_members()
    log("INFO", f"Already collected: {len(saved_members)} members")

    app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH, no_updates=True)
    await app.start()
    log("INFO", "Session started")

    for i, group in enumerate(sources):
        log("INFO", f"[{i+1}/{len(sources)}] Processing {group}...")

        try:
            await app.join_chat(group)
            await asyncio.sleep(3)
            log("OK", f"Joined {group}")
        except Exception as e:
            log("SKIP", f"Cannot join {group}: {str(e)[:60]}")
            continue

        try:
            members_count = 0
            async for member in app.get_chat_members(group):
                user = member.user
                if not user.is_bot and not user.is_deleted and user.username:
                    saved_members.add(user.username.lower())
                    members_count += 1

                if members_count >= 200:
                    break

            log("OK", f"Got {members_count} members from {group}")
            save_members(saved_members)

        except FloodWait as e:
            log("FLOOD", f"Flood wait {e.value}s while scraping")
            await asyncio.sleep(e.value)
        except Exception as e:
            log("ERR", f"Scrape error in {group}: {str(e)[:60]}")

        try:
            await app.leave_chat(group)
        except Exception:
            pass

        await asyncio.sleep(delay)

    log("INFO", f"Total collected: {len(saved_members)} unique members")
    log("INFO", "Starting to add members to target group...")

    members_list = list(saved_members)
    added = 0
    for i, username in enumerate(members_list):
        try:
            if not username.startswith("@"):
                username = "@" + username
            await app.add_chat_members(target, username)
            added += 1
            log("ADDED", f"[{i+1}/{len(members_list)}] Added @{username.replace('@','')}")
        except FloodWait as e:
            log("FLOOD", f"Flood wait {e.value}s")
            await asyncio.sleep(e.value)
            continue
        except UserChannelsTooMuch:
            log("WARN", "Too many groups, taking 60s break...")
            await asyncio.sleep(60)
            continue
        except UserNotMutualContact:
            log("SKIP", f"@{username.replace('@','')} privacy blocked")
        except Exception as e:
            err = str(e)[:60]
            if "USER_ID_INVALID" in err or "USERNAME_INVALID" in err:
                log("DEAD", f"@{username.replace('@','')} invalid")
            elif "USER_ALREADY_PARTICIPANT" in err:
                log("SKIP", f"@{username.replace('@','')} already in group")
            else:
                log("FAIL", f"@{username.replace('@','')}: {err}")

        await asyncio.sleep(3)

    log("INFO", f"Done! Added {added} members to {target}")
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
