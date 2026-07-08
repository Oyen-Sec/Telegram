#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import sys
from pyrogram import Client
import config

SESSION_NAME = sys.argv[1] if len(sys.argv) > 1 else "lazarus"

async def main():
    print(f"Creating session: {SESSION_NAME}")
    print("Enter phone number + code when prompted...")
    app = Client(SESSION_NAME, api_id=config.API_ID, api_hash=config.API_HASH)
    await app.start()
    me = await app.get_me()
    print(f"\n✅ Login success!")
    print(f"   Name: {me.first_name}")
    print(f"   Username: @{me.username}")
    print(f"   ID: {me.id}")
    print(f"   Session file: {SESSION_NAME}.session")
    await app.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
