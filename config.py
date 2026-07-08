import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8893031967:AAFB2xpKJSLzF7HhIAs0V5PMVccmSLKInE4")
TARGET_GROUP = os.getenv("TARGET_GROUP", "@LazarusDdos")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", 1896515340))
MAX_ADD_PER_DAY = int(os.getenv("MAX_ADD_PER_DAY", 50))
SOURCES_FILE = os.path.join(os.path.dirname(__file__), "sources.txt")
PROXIES_FILE = os.path.join(os.path.dirname(__file__), "proxies.txt")
DB_FILE = os.path.join(os.path.dirname(__file__), "progress.db")
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), "checkpoint.json")
SESSION_NAME = os.getenv("SESSION_NAME", "lazarus")
SESSION_BASE = os.path.join(os.path.dirname(__file__), SESSION_NAME)
JITTER_MIN = 10
JITTER_MAX = 20
BATCH_JITTER_MIN = 30
BATCH_JITTER_MAX = 60
BATCH_SIZE = 5
LONG_PAUSE_AFTER = 20
LONG_PAUSE_MIN = 120
LONG_PAUSE_MAX = 300
MAX_RETRIES = 3
NOTIFY_EVERY = 10
