import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait, UserAlreadyParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid
from utils import log, format_number
from database import add_member, member_exists, get_total_unique

async def scrape_group(app: Client, source_group: str, leave_after=True):
    log("INFO", f"Processing {source_group}...")

    try:
        chat = await app.get_chat(source_group)
    except UsernameNotOccupied:
        log("ERROR", f"Group {source_group} not found")
        return 0
    except FloodWait as e:
        log("FLOOD", f"Flood wait {e.value}s before getting chat {source_group}")
        await asyncio.sleep(e.value)
        try:
            chat = await app.get_chat(source_group)
        except Exception as e2:
            log("ERROR", f"Failed to get chat {source_group}: {e2}")
            return 0
    except Exception as e:
        log("ERROR", f"Failed to get chat {source_group}: {e}")
        return 0

    try:
        await app.join_chat(source_group)
        log("SUCCESS", f"Joined {source_group} | Members: {format_number(chat.members_count if chat.members_count else 0)}")
    except UserAlreadyParticipant:
        log("INFO", f"Already joined {source_group}")
    except FloodWait as e:
        log("FLOOD", f"Flood wait {e.value}s before joining {source_group}")
        await asyncio.sleep(e.value)
        try:
            await app.join_chat(source_group)
            log("SUCCESS", f"Joined {source_group} after flood wait")
        except Exception as e2:
            log("ERROR", f"Failed to join {source_group} after flood: {e2}")
            return 0
    except Exception as e:
        log("ERROR", f"Failed to join {source_group}: {e}")
        return 0

    await asyncio.sleep(2)

    scraped = 0
    try:
        async for member in app.get_chat_members(source_group):
            if scraped > 0 and scraped % 200 == 0:
                log("PROGRESS", f"{source_group} | Scraped: {format_number(scraped)}")

            user = member.user
            if user and not user.is_deleted and not user.is_bot:
                if not member_exists(user.id):
                    add_member(user.id, user.username, user.first_name, user.last_name, source_group)
                scraped += 1

            await asyncio.sleep(0.05)
    except FloodWait as e:
        log("FLOOD", f"Flood wait {e.value}s while scraping {source_group}")
        await asyncio.sleep(e.value)
    except Exception as e:
        log("ERROR", f"Error scraping {source_group}: {e}")

    total_unique = get_total_unique()
    log("SUCCESS", f"Scraped {format_number(scraped)} members from {source_group} | Total unique: {format_number(total_unique)}")

    if leave_after:
        try:
            await app.leave_chat(source_group)
            log("INFO", f"Left {source_group}")
        except Exception as e:
            log("ERROR", f"Failed to leave {source_group}: {e}")

    return scraped
