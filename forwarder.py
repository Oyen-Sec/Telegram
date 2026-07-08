#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
import random
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, ChatWriteForbidden, UserChannelsTooMuch, UsernameNotOccupied, PeerIdInvalid
from utils import log, load_sources
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

running = True

async def main():
    global running

    if len(sys.argv) < 4:
        print("Usage: python forwarder.py <source_chat> <message_id> <delay_seconds> [cycle_delay] [target]")
        print("  delay       = seconds between each group")
        print("  cycle_delay = seconds between full rounds (default 300 = 5 min)")
        print("  target      = single group (omits sources.txt)")
        print("Examples:")
        print("  python forwarder.py @LazarusDdos 85 60")
        print("  python forwarder.py @LazarusDdos 85 60 300 @testgroup")
        sys.exit(1)

    source_chat = sys.argv[1]
    message_id = int(sys.argv[2])
    delay = int(sys.argv[3])
    cycle_delay = int(sys.argv[4]) if len(sys.argv) >= 5 else 300

    if len(sys.argv) >= 6:
        sources = [sys.argv[5]]
        cycle_delay = 0
        log("INFO", f"Single target: {sources[0]}")
    else:
        sources = load_sources(config.SOURCES_FILE)
        if not sources:
            log("ERROR", "No target groups in sources.txt")
            sys.exit(1)

    log("INFO", f"Source: {source_chat}, Message ID: {message_id}")
    log("INFO", f"Targets: {len(sources)} groups, Delay: {delay}s, Cycle delay: {cycle_delay}s")

    async def start_client():
        try:
            app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
            await app.start()
            return app
        except Exception as e:
            log("ERROR", f"Failed to start client: {e}")
            return None

    app = await start_client()
    if not app:
        return

    async def restart_client():
        nonlocal app
        try:
            await app.stop()
        except Exception:
            pass
        await asyncio.sleep(3)
        app = await start_client()
        return app is not None

    async def join_and_forward(target):
        already_joined = False
        for attempt in range(2):
            try:
                await app.forward_messages(target, source_chat, [message_id])
                return True
            except FloodWait as e:
                raise e
            except (UsernameNotOccupied, PeerIdInvalid):
                return False
            except ChatWriteForbidden:
                if not already_joined:
                    try:
                        await app.join_chat(target)
                        await asyncio.sleep(random.randint(2, 5))
                        already_joined = True
                        continue
                    except Exception:
                        return False
                return False
            except (OSError, ConnectionError, TimeoutError) as e:
                log("WARN", f"Connection lost: {str(e)[:50]}. Reconnecting...")
                ok = await restart_client()
                if not ok:
                    return False
                continue
            except Exception as e:
                log("FAIL", f"{target}: {str(e)[:80]}")
                return False
        return False

    while running:
        total = len(sources)
        for i, group in enumerate(sources):
            if not running:
                break
            try:
                success = await join_and_forward(group)
                if success:
                    log("SUCCESS", f"[{i + 1}/{total}] Sent to {group}")
                else:
                    log("SKIP", f"[{i + 1}/{total}] Cannot send to {group}")
            except FloodWait as e:
                log("FLOOD", f"Flood wait {e.value}s")
                await asyncio.sleep(min(e.value, 3600))
                if e.value > 60:
                    log("INFO", "Reconnecting after flood wait...")
                    ok = await restart_client()
                    if not ok:
                        break
                if e.value > 3600:
                    log("WARN", f"Long flood ({e.value}s), continuing anyway...")
            except UserChannelsTooMuch:
                log("ERROR", "Too many groups joined")
                running = False
                break
            except (OSError, ConnectionError) as e:
                log("WARN", f"Socket error in loop: {str(e)[:50]}. Reconnecting...")
                ok = await restart_client()
                if not ok:
                    break

            if running:
                jitter = random.uniform(0.5, 1.5)
                await asyncio.sleep(delay * jitter)

        if running and cycle_delay > 0:
            log("INFO", f"Cycle done. Waiting {cycle_delay}s before next round...")
            await asyncio.sleep(cycle_delay)
            log("INFO", "Starting next cycle...")

    try:
        await app.stop()
    except Exception:
        pass
    log("INFO", "Forwarder stopped")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
