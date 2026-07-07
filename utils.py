import os
import random
import time
import asyncio
from colorama import init, Fore, Style

init(autoreset=True)

LOG_COLORS = {
    "SUCCESS": Fore.GREEN,
    "ERROR": Fore.RED,
    "FAIL": Fore.RED,
    "WAIT": Fore.YELLOW,
    "PENDING": Fore.YELLOW,
    "INFO": Fore.CYAN,
    "PROGRESS": Fore.CYAN,
    "SKIP": Fore.YELLOW,
    "FLOOD": Fore.RED,
}

def log(level, message):
    color = LOG_COLORS.get(level.upper(), Fore.WHITE)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] [{level.upper()}] {message}{Style.RESET_ALL}")

def jitter(min_sec, max_sec):
    return random.uniform(min_sec, max_sec)

async def async_sleep(min_sec, max_sec=None):
    if max_sec is None:
        await asyncio.sleep(min_sec)
    else:
        await asyncio.sleep(jitter(min_sec, max_sec))

def parse_source_group(raw):
    raw = raw.strip()
    if not raw:
        return None
    if raw.startswith("https://t.me/addlist/"):
        return raw
    if raw.startswith("t.me/"):
        return raw.replace("t.me/", "@")
    if raw.startswith("https://t.me/"):
        return "@" + raw.split("/")[-1]
    if raw.startswith("@"):
        return raw
    return f"@{raw}"

def load_sources(path):
    if not os.path.exists(path):
        log("ERROR", f"Sources file not found: {path}")
        return []
    sources = []
    with open(path, "r") as f:
        for line in f:
            parsed = parse_source_group(line)
            if parsed:
                sources.append(parsed)
    return sources

def load_proxies(path):
    if not os.path.exists(path):
        return []
    proxies = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                proxies.append(line)
    return proxies

def format_number(n):
    if n >= 1000:
        return f"{n:,}"
    return str(n)
