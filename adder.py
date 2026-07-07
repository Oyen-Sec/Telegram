import asyncio
from pyrogram import Client
from pyrogram.errors import (
    FloodWait, UserAlreadyParticipant, UserNotMutualContact,
    UserPrivacyRestricted, PeerIdInvalid, UsernameNotOccupied,
    ChatAdminRequired, UserChannelsTooMuch
)
from utils import log, jitter, format_number
from database import (
    get_pending_members, update_member_status, get_daily_add_count,
    increment_daily_counter, get_stats, save_checkpoint, load_checkpoint,
    clear_checkpoint
)
import config

async def send_bot_notification(bot, message):
    if bot is None:
        return
    try:
        await bot.send_message(config.OWNER_CHAT_ID, message)
    except Exception as e:
        log("ERROR", f"Failed to send bot notification: {e}")

def format_progress_report(stats, current, total):
    pct = (current / total * 100) if total > 0 else 0
    return (
        "\U0001f4ca LAZARUS PROGRESS REPORT\n"
        "\u2500" * 21 + "\n"
        f"Phase: Adding Members\n"
        f"Target: {config.TARGET_GROUP}\n"
        f"Progress: {current}/{total} ({pct:.1f}%)\n"
        f"Success: {stats['added']} | Failed: {stats['failed']}\n"
        f"Status: Running"
    )

async def add_loop(app: Client, bot=None):
    stats = get_stats()
    total_to_add = stats["pending"]
    if total_to_add == 0:
        if stats["added"] > 0:
            log("INFO", "No pending members to add. All done!")
        else:
            log("INFO", "No members in database. Run --scrape-only first.")
        return

    log("INFO", f"Starting add phase: {format_number(total_to_add)} members to add")
    log("INFO", f"Daily add limit: {config.MAX_ADD_PER_DAY}")

    daily_count = get_daily_add_count()
    if daily_count >= config.MAX_ADD_PER_DAY:
        log("WAIT", f"Daily limit reached ({daily_count}/{config.MAX_ADD_PER_DAY})")
        if bot:
            await send_bot_notification(bot,
                f"\u26a0\ufe0f DAILY LIMIT REACHED\n"
                f"Today: {daily_count}/{config.MAX_ADD_PER_DAY}\n"
                f"Resume tomorrow or increase MAX_ADD_PER_DAY."
            )
        return

    members = get_pending_members()
    batch = []
    last_notify_count = 0
    human_like_count = 0

    for idx, member in enumerate(members):
        daily_count = get_daily_add_count()
        if daily_count >= config.MAX_ADD_PER_DAY:
            log("WAIT", f"Daily limit reached ({daily_count}/{config.MAX_ADD_PER_DAY})")
            save_checkpoint({"phase": "add", "last_index": idx})
            if bot:
                await send_bot_notification(bot,
                    f"\u26a0\ufe0f DAILY LIMIT REACHED\n"
                    f"Today: {daily_count}/{config.MAX_ADD_PER_DAY}\n"
                    f"Script paused. Resume tomorrow."
                )
            break

        try:
            await app.add_chat_members(config.TARGET_GROUP, member["user_id"])
            update_member_status(member["user_id"], "added")
            increment_daily_counter()
            batch.append(member)
            log("SUCCESS", f"Added {member['user_id']} ({member['username'] or 'no username'}) | {idx + 1}/{total_to_add}")

            stats = get_stats()
            if stats["added"] - last_notify_count >= config.NOTIFY_EVERY:
                last_notify_count = stats["added"]
                if bot:
                    msg = format_progress_report(stats, stats["added"], total_to_add)
                    await send_bot_notification(bot, msg)

            human_like_count += 1
            if human_like_count >= config.LONG_PAUSE_AFTER:
                pause = jitter(config.LONG_PAUSE_MIN, config.LONG_PAUSE_MAX)
                log("WAIT", f"Human-like pause: {pause:.0f}s after {human_like_count} adds")
                await asyncio.sleep(pause)
                human_like_count = 0
            else:
                delay = jitter(config.JITTER_MIN, config.JITTER_MAX)
                log("WAIT", f"Jitter: {delay:.0f}s before next user...")
                await asyncio.sleep(delay)

        except FloodWait as e:
            update_member_status(member["user_id"], "pending", f"flood_wait_{e.value}s")
            log("FLOOD", f"Flood wait {e.value}s for user {member['user_id']}")
            if bot:
                await send_bot_notification(bot,
                    f"\U0001f4a7 FLOOD WAIT\n"
                    f"User: {member['user_id']}\n"
                    f"Duration: {e.value}s\n"
                    f"Pausing..."
                )
            await asyncio.sleep(e.value)

        except UserAlreadyParticipant:
            update_member_status(member["user_id"], "skipped", "already_member")
            log("SKIP", f"{member['user_id']} already member")
            await asyncio.sleep(jitter(2, 5))

        except UserPrivacyRestricted:
            update_member_status(member["user_id"], "skipped", "privacy_restricted")
            log("SKIP", f"{member['user_id']} privacy restricted")
            await asyncio.sleep(jitter(2, 5))

        except UserNotMutualContact:
            update_member_status(member["user_id"], "skipped", "not_mutual_contact")
            log("SKIP", f"{member['user_id']} not mutual contact")
            await asyncio.sleep(jitter(2, 5))

        except PeerIdInvalid:
            update_member_status(member["user_id"], "failed", "peer_id_invalid")
            log("ERROR", f"{member['user_id']} invalid peer")
            await asyncio.sleep(jitter(2, 5))

        except UserChannelsTooMuch:
            log("ERROR", "Joined too many channels/groups. Need to leave some first.")
            if bot:
                await send_bot_notification(bot,
                    "\u274c TOO MANY CHANNELS\n"
                    "Account has joined too many groups. Leave some and retry."
                )
            break

        except ChatAdminRequired:
            update_member_status(member["user_id"], "failed", "chat_admin_required")
            log("ERROR", f"Admin rights required to add members to {config.TARGET_GROUP}. Stopping.")
            if bot:
                await send_bot_notification(bot,
                    f"\u274c ADMIN REQUIRED\n"
                    f"Account needs admin rights in {config.TARGET_GROUP} to add members."
                )
            break

        except Exception as e:
            error_str = str(e)
            if "USER_ALREADY_PARTICIPANT" in error_str.upper():
                update_member_status(member["user_id"], "skipped", "already_member")
                log("SKIP", f"{member['user_id']} already member")
            elif "PRIVACY" in error_str.upper():
                update_member_status(member["user_id"], "skipped", "privacy_restricted")
                log("SKIP", f"{member['user_id']} privacy restricted")
            elif "USER_NOT_MUTUAL_CONTACT" in error_str.upper():
                update_member_status(member["user_id"], "skipped", "not_mutual_contact")
                log("SKIP", f"{member['user_id']} not mutual contact")
            elif "USERNAME_NOT_OCCUPIED" in error_str.upper():
                update_member_status(member["user_id"], "failed", "username_invalid")
                log("SKIP", f"{member['user_id']} invalid username")
            elif "USER_ALREADY_INVITED" in error_str.upper():
                update_member_status(member["user_id"], "skipped", "already_invited")
                log("SKIP", f"{member['user_id']} already invited")
            elif "CHAT_ADMIN_REQUIRED" in error_str.upper():
                log("ERROR", f"Admin rights required. Stopping.")
                if bot:
                    await send_bot_notification(bot, "\u274c ADMIN REQUIRED")
                break
            elif "PHONE_NUMBER_BANNED" in error_str.upper():
                log("ERROR", "ACCOUNT BANNED! Stopping all operations.")
                if bot:
                    await send_bot_notification(bot, "\u274c ACCOUNT BANNED")
                return
            elif "FLOOD" in error_str.upper():
                update_member_status(member["user_id"], "pending", "flood_wait")
                log("FLOOD", f"Flood wait detected, pausing 60s")
                await asyncio.sleep(60)
            else:
                update_member_status(member["user_id"], "failed", error_str[:200])
                log("ERROR", f"Failed to add {member['user_id']}: {error_str[:120]}")
            await asyncio.sleep(jitter(2, 5))

        if len(batch) >= config.BATCH_SIZE:
            delay = jitter(config.BATCH_JITTER_MIN, config.BATCH_JITTER_MAX)
            log("WAIT", f"Batch complete ({len(batch)} users). Pausing {delay:.0f}s...")
            await asyncio.sleep(delay)
            batch = []

    stats = get_stats()
    log("SUCCESS", f"Add complete. Added: {stats['added']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")

    if stats["pending"] == 0:
        clear_checkpoint()
    else:
        save_checkpoint({"phase": "add", "pending_remaining": stats["pending"]})

    if bot:
        pct = (stats["added"] / (total_to_add or 1)) * 100
        await send_bot_notification(bot,
            f"\u2705 ADD PHASE COMPLETE\n"
            f"Added: {stats['added']}\n"
            f"Failed: {stats['failed']}\n"
            f"Skipped: {stats['skipped']}\n"
            f"Progress: {pct:.1f}%"
        )
