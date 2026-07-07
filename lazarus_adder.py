#!/usr/bin/env python3
import argparse
import asyncio
import sys
import os
import signal
import logging
from pyrogram import Client
from utils import log, jitter, async_sleep, load_sources
from database import init_db, save_checkpoint, load_checkpoint, clear_checkpoint, get_stats
from scraper import scrape_group
from adder import add_loop, send_bot_notification
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

running = True

def signal_handler(sig, frame):
    global running
    if running:
        log("INFO", "Shutdown signal received. Saving checkpoint for resume...")
        running = False

async def main():
    global running

    parser = argparse.ArgumentParser(description="Lazarus Telegram Member Scraper & Adder")
    parser.add_argument("--start", action="store_true", help="Start from scratch (clear checkpoint)")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--scrape-only", action="store_true", help="Only scrape members, skip adding")
    parser.add_argument("--add-only", action="store_true", help="Only add members from existing DB")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    init_db()
    log("INFO", "Starting Lazarus Member Adder")

    if not config.API_ID or not config.API_HASH:
        log("ERROR", "API_ID and API_HASH must be set in .env file")
        log("INFO", "Create a .env file in the lazarus_adder directory with:")
        log("INFO", "  API_ID=your_api_id")
        log("INFO", "  API_HASH=your_api_hash")
        return

    if args.start:
        clear_checkpoint()
        checkpoint = {"phase": "scrape", "current_index": 0}
        log("INFO", "Starting fresh session")
    elif args.resume:
        checkpoint = load_checkpoint()
        if not checkpoint:
            log("INFO", "No checkpoint found. Starting from scratch.")
            checkpoint = {"phase": "scrape", "current_index": 0}
        else:
            log("INFO", f"Resuming from checkpoint: {checkpoint}")
    elif args.scrape_only:
        checkpoint = {"phase": "scrape", "current_index": 0}
    elif args.add_only:
        checkpoint = {"phase": "add"}

    sources = load_sources(config.SOURCES_FILE)
    log("INFO", f"Loaded {len(sources)} source groups")

    bot = None
    if config.BOT_TOKEN:
        try:
            bot = Client("bot_session", bot_token=config.BOT_TOKEN, in_memory=True, api_id=config.API_ID, api_hash=config.API_HASH)
            await bot.start()
            log("INFO", "Bot notification client started")
        except Exception as e:
            log("ERROR", f"Failed to start bot client: {e}")
            bot = None

    try:
        app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
        await app.start()
        log("INFO", "User session started")
    except Exception as e:
        log("ERROR", f"Failed to start user client: {e}")
        if bot:
            await bot.stop()
        return

    current_idx = checkpoint.get("current_index", 0) if checkpoint.get("phase") == "scrape" else 0

    try:
        if checkpoint.get("phase") == "scrape" and not args.add_only:
            start_idx = current_idx
            for i, source in enumerate(sources[start_idx:], start=start_idx):
                if not running:
                    break

                log("INFO", f"Group {i + 1}/{len(sources)}: {source}")
                await scrape_group(app, source, leave_after=True)

                save_checkpoint({"phase": "scrape", "current_index": i + 1})

                if i < len(sources) - 1 and running:
                    await async_sleep(3, 7)

            log("SUCCESS", "Scraping phase complete")

            if not args.scrape_only and running:
                checkpoint = {"phase": "add"}
                save_checkpoint(checkpoint)

        if checkpoint.get("phase") == "add" and running and not args.scrape_only:
            stats = get_stats()
            if stats["pending"] > 0:
                await add_loop(app, bot)
            elif stats["added"] > 0:
                log("INFO", "All members already added to target group")
            else:
                log("INFO", "No members to add. Run --scrape-only first to populate database.")

    except Exception as e:
        log("ERROR", f"Fatal error: {str(e)[:200]}")
        save_checkpoint({"phase": "scrape", "current_index": current_idx})
        if bot:
            await send_bot_notification(bot, f"\u274c FATAL ERROR\n{str(e)[:200]}")

    finally:
        await app.stop()
        if bot:
            await bot.stop()
        log("INFO", "Lazarus Member Adder stopped")

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
    except Exception as e:
        log("ERROR", f"Unhandled error: {e}")
