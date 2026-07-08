#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait
from utils import log, async_sleep
import config

logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrogram.client").setLevel(logging.ERROR)

SOURCES_FILE = config.SOURCES_FILE

KEYWORDS = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "id", "my", "us", "me", "go", "no", "up", "in", "it", "to", "of",
    "is", "on", "at", "by", "or", "be", "he", "we", "an", "as", "do",
    "so", "if", "am", "ax", "ok", "tv", "fx", "vs",
    "ai", "oo", "ee", "ll", "uu", "pp", "yy", "tt", "ss", "bb",
    "the", "and", "for", "are", "but", "not", "you", "all", "can",
    "had", "her", "was", "one", "our", "out", "has", "have", "had",
    "its", "new", "now", "old", "see", "way", "who", "bin", "did",
    "get", "got", "hit", "let", "put", "run", "say", "set", "she",
    "too", "use", "add", "ask", "buy", "cry", "die", "eat", "end",
    "pay", "sit", "win", "age", "ago", "air", "arm", "art", "bad",
    "bag", "bar", "bed", "big", "bit", "box", "boy", "bus", "can",
    "cap", "car", "cat", "cup", "cut", "dad", "day", "did", "dog",
    "dot", "dry", "ear", "east", "eat", "egg", "end", "era", "eve",
    "eye", "fan", "far", "fat", "few", "fit", "fix", "fly", "for",
    "fox", "fun", "gap", "gas", "god", "gun", "guy", "hat", "hit",
    "hot", "how", "ice", "ill", "job", "joy", "key", "kid", "kit",
    "lab", "law", "lay", "leg", "let", "lie", "lip", "lot", "low",
    "mad", "man", "map", "may", "men", "mix", "mom", "net", "nor",
    "now", "nut", "odd", "off", "oil", "old", "own", "pet", "pie",
    "pin", "pit", "pop", "pot", "put", "raw", "red", "rid", "row",
    "rub", "rug", "sad", "sat", "saw", "say", "sea", "she", "sir",
    "sit", "six", "sky", "son", "sun", "tab", "tap", "tax", "tea",
    "ten", "the", "tie", "tin", "tip", "toe", "ton", "too", "top",
    "toy", "try", "two", "use", "van", "war", "was", "wax", "way",
    "web", "wet", "who", "why", "win", "wit", "won", "yes", "yet",
    "you", "zero", "zone", "zoom", "zoo",
    "free", "fire", "pubg", "ml", "ff", "game", "play", "sport",
    "movie", "film", "music", "song", "art", "photo", "video",
    "news", "info", "blog", "vlog", "live", "stream", "tv",
    "shop", "store", "market", "buy", "sell", "deal", "price",
    "love", "life", "work", "job", "career", "study", "learn",
    "school", "college", "univ", "course", "class", "group",
    "chat", "talk", "discuss", "forum", "room", "channel",
    "indonesia", "indo", "jakarta", "bandung", "surabaya",
    "jawa", "sumatra", "sulawesi", "kalimantan", "papua",
    "bali", "medan", "makassar", "semarang", "yogyakarta",
    "webshell", "cpanel", "shell", "seo", "ddos", "hack",
    "crack", "exploit", "malware", "virus", "trojan", "spam",
    "phish", "carding", "darkweb", "scam", "fraud", "cheat",
    "bot", "panel", "server", "vps", "rdp", "vpn", "proxy",
    "smtp", "mailer", "tools", "script", "code", "dev",
    "python", "php", "java", "js", "html", "css", "sql",
    "api", "botnet", "backdoor", "shellback", "bypass",
    "inject", "payload", "encoded", "obfuscate", "crypto",
    "bitcoin", "bnb", "ethereum", "wallet", "blockchain",
    "nft", "defi", "airdrop", "mining", "trading", "signal",
    "forex", "stock", "option", "investment", "profit",
    "money", "income", "passive", "bisnis", "online",
    "marketing", "affiliate", "mlm", "reseller", "dropship",
    "loker", "kerja", "lowongan", "kerja", "freelance",
    "remote", "wfh", "digital", "creator", "content",
    "promo", "diskon", "gratis", "voucher", "cashback",
    "giveaway", "lucky", "draw", "win", "bonus", "reward",
    "bokep", "viral", "hot", "sexy", "dewasa", "18+",
    "colmek", "memek", "kontol", "nude", "telanjang",
    "asmr", "sange", "ngentot", "sex", "porno",
    "anime", "manga", "manhwa", "cartoon", "cosplay",
    "drakor", "drama", "korea", "jepang", "china",
    "streaming", "nonton", "download", "subtitle", "indo",
    "meme", "lucu", "humor", "funny", "joke", "comedy",
    "quotes", "motivasi", "inspirasi", "islam", "muslim",
    "ngaji", "quran", "hadist", "doa", "sholat", "puasa",
    "otomotif", "motor", "mobil", "modif", "balap",
    "travel", "liburan", "wisata", "hotel", "tiket",
    "makanan", "resep", "masak", "kue", "minuman",
    "kesehatan", "sehat", "obat", "dokter", "rumah sakit",
    "fashion", "baju", "sepatu", "tas", "aksesoris",
    "kecantikan", "makeup", "skincare", "hair", "nails",
    "olahraga", "gym", "fitness", "workout", "yoga",
    "tanaman", "kebun", "berkebun", "hidroponik",
    "hewan", "kucing", "anjing", "burung", "ikan",
    "fotografi", "kamera", "edit", "desain", "graphic",
    "teknologi", "gadget", "hp", "android", "iphone",
    "komputer", "laptop", "pc", "gaming", "console",
    "musik", "band", "vocal", "instrument", "dj",
    "sastra", "puisi", "cerpen", "novel", "buku",
    "politik", "berita", "info", "update", "breaking",
    "pendidikan", "sd", "smp", "sma", "kuliah", "beasiswa",
    "bisnis", "wirausaha", "usaha", "startup", "ukm",
    "properti", "rumah", "tanah", "apartemen", "kontrakan",
    "investasi", "saham", "reksadana", "emas", "crypto",
    "asuransi", "pajak", "keuangan", "finance", "bank",
    "ecommerce", "tokopedia", "shopee", "lazada", "bukalapak",
    "sosial", "media", "facebook", "instagram", "tiktok",
    "youtube", "twitter", "discord", "telegram", "whatsapp",
]

running = True

async def main():
    global running

    app = Client(config.SESSION_BASE, api_id=config.API_ID, api_hash=config.API_HASH)
    await app.start()
    log("INFO", "Session started")

    existing = set()
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip().replace("@", "").lower()
                if line:
                    existing.add(line)

    all_new = set()

    for kw in KEYWORDS:
        if not running:
            break
        log("INFO", f"Searching: '{kw}'...")
        try:
            count = 0
            async for msg in app.search_global(kw, limit=50):
                chat = msg.chat
                if chat and chat.username:
                    u = chat.username.lower()
                    if u not in existing and u not in all_new:
                        all_new.add(u)
                        count += 1
            log("SUCCESS", f"  '{kw}': found {count} new groups")
            await async_sleep(3, 6)
        except FloodWait as e:
            log("FLOOD", f"Flood wait {e.value}s")
            await asyncio.sleep(e.value)
        except Exception as e:
            log("ERROR", f"  '{kw}': {str(e)[:80]}")
            await asyncio.sleep(5)

    if all_new:
        with open(SOURCES_FILE, "a", encoding="utf-8") as f:
            for u in sorted(all_new):
                f.write(f"@{u}\n")
        total_new = len(all_new)
        total_all = len(existing) + total_new
        log("SUCCESS", f"Added {total_new} new groups from search")
        log("INFO", f"Total: {total_all} groups")
    else:
        log("INFO", "No new groups found via search")

    await app.stop()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log("INFO", "Interrupted by user")
