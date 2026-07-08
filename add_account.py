#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
import os
from pyrogram import Client
import config

if len(sys.argv) < 2:
    print("Usage: python add_account.py <session_name>")
    print("Example: python add_account.py akun1")
    sys.exit(1)

name = sys.argv[1]

async def main():
    app = Client(name, api_id=config.API_ID, api_hash=config.API_HASH, no_updates=True)
    print(f"Creating session: {name}")
    print("Enter phone number and code when prompted...")
    await app.start()
    me = await app.get_me()
    print(f"\n✅ {me.first_name} (@{me.username}) - ID: {me.id}")
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
