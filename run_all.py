#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-account forwarder.
Splits sources.txt across N accounts, runs them in parallel.
Usage: python run_all.py <source_chat> <message_id> <delay> <cycle_delay> <sources_file>
Example: python run_all.py @LazarusDdos 85 60 300 sources2.txt
"""
import asyncio
import sys
import os
import math
import signal
import subprocess
import random
from utils import log, load_sources
import config

# List of session names (accounts)
ACCOUNTS = ["akun1", "akun2", "akun3", "akun4", "akun5"]

async def main():
    if len(sys.argv) < 5:
        print("Usage: python run_all.py <source_chat> <message_id> <delay> <cycle_delay> <sources_file>")
        sys.exit(1)

    source_chat = sys.argv[1]
    msg_id = sys.argv[2]
    delay = sys.argv[3]
    cycle_delay = sys.argv[4]
    sources_file = sys.argv[5] if len(sys.argv) > 5 else config.SOURCES_FILE

    # Check which accounts have session files
    available = []
    for acc in ACCOUNTS:
        session_file = os.path.join(os.path.dirname(__file__), f"{acc}.session")
        if os.path.exists(session_file):
            available.append(acc)

    if not available:
        log("ERROR", "No accounts found! Run: python add_account.py akun1")
        sys.exit(1)

    log("INFO", f"Available accounts: {', '.join(available)} ({len(available)} total)")

    # Load sources
    all_sources = load_sources(sources_file)
    if not all_sources:
        log("ERROR", f"No groups in {sources_file}")
        sys.exit(1)

    # Shuffle and split sources evenly
    random.shuffle(all_sources)
    chunk_size = math.ceil(len(all_sources) / len(available))
    chunks = [all_sources[i:i+chunk_size] for i in range(0, len(all_sources), chunk_size)]

    processes = []
    for i, (acc, chunk) in enumerate(zip(available, chunks)):
        if not chunk:
            continue
        tmp_file = f"sources_{acc}.txt"
        tmp_path = os.path.join(os.path.dirname(__file__), tmp_file)
        with open(tmp_path, "w") as f:
            f.write("\n".join(chunk) + "\n")

        log("INFO", f"[{acc}] {len(chunk)} groups -> {tmp_file}")
        
        cmd = [
            sys.executable, "forwarder.py",
            source_chat, msg_id, delay, cycle_delay, tmp_file
        ]
        
        # Stagger start by i * 30 seconds to avoid simultaneous joins
        env = os.environ.copy()
        env["SESSION_BASE"] = os.path.join(os.path.dirname(__file__), acc)
        
        p = await asyncio.create_subprocess_exec(
            *cmd, env=env,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        processes.append((acc, p))
        log("INFO", f"[{acc}] Started (PID: {p.pid}), staggering +{i*30}s")
        await asyncio.sleep(30)  # stagger starts

    log("INFO", f"All {len(processes)} accounts running. Waiting...")
    
    # Wait for any to finish
    for acc, p in processes:
        await p.wait()
        log("WARN", f"[{acc}] Stopped unexpectedly")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Shutting down all accounts...")
