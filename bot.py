import asyncio
import os
import aiosqlite
from datetime import datetime, timedelta, timezone
from typing import Optional
import html


from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ChatPermissions
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()
DB_PATH = os.path.join(os.path.dirname(__file__), "forwards.db")
BOT_TOKEN = os.getenv("BOT_TOKEN")

router = Router()


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        # Check existing schema
        try:
            async with db.execute("PRAGMA table_info(forward_counts)") as cursor:
                rows = await cursor.fetchall()
        except Exception:
            rows = []

        if not rows:
            # Table does not exist: create with the latest schema
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS forward_counts (
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    date    TEXT    NOT NULL,
                    count   INTEGER NOT NULL,
                    PRIMARY KEY (chat_id, user_id, date)
                );
                """
            )
            # Events table: log every violation timestamp (UTC, seconds precision)
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS forward_events (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    ts      TEXT    NOT NULL
                );
                """
            )
            await db.commit()
            return

        # Table exists: migrate if 'date' column is missing
        existing_columns = {r[1] for r in rows}
        if "date" not in existing_columns:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS forward_counts_new (
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    date    TEXT    NOT NULL,
                    count   INTEGER NOT NULL,
                    PRIMARY KEY (chat_id, user_id, date)
                );
                """
            )
            today = get_today_date()
            # Migrate old aggregated counts to today's date
            await db.execute(
                """
                INSERT INTO forward_counts_new (chat_id, user_id, date, count)
                SELECT chat_id, user_id, ?, count FROM forward_counts
                """,
                (today,),
            )
            await db.execute("DROP TABLE forward_counts")
            await db.execute("ALTER TABLE forward_counts_new RENAME TO forward_counts")
            # Ensure events table exists after migration as well
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS forward_events (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    ts      TEXT    NOT NULL
                );
                """
            )
            await db.commit()
        # If 'date' exists, nothing to do
        # Also ensure events table exists (idempotent)
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS forward_events (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                ts      TEXT    NOT NULL
            );
            """
        )
        await db.commit()


def get_today_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_current_timestamp_utc() -> str:
    # ISO-8601 without microseconds, with Z suffix, seconds precision
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_current_timestamp_local_ms() -> str:
    # Local time with milliseconds precision in format YYYY-MM-DD HH:MM:SS.mmm
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def format_forward_source_html(message: Message) -> str:
    """Return HTML-formatted forward source. If we can build a clickable link, do so."""
    origin = getattr(message, "forward_origin", None)
    try:
        # Channel origin
        chat = getattr(origin, "chat", None)
        if chat is not None and getattr(chat, "title", None):
            title = html.escape(str(chat.title))
            username = getattr(chat, "username", None)
            if username:
                href = f"https://t.me/{username}"
                return f'<a href="{href}">{title}</a>'
            return title
        # User origin (real user)
        sender_user = getattr(origin, "sender_user", None)
        if sender_user is not None and getattr(sender_user, "full_name", None):
            full_name = html.escape(str(sender_user.full_name))
            uid = getattr(sender_user, "id", None)
            if uid:
                return f'<a href="tg://user?id={uid}">{full_name}</a>'
            return full_name
        # Hidden user origin
        hidden_name = getattr(origin, "sender_user_name", None)
        if hidden_name:
            return html.escape(str(hidden_name))
        # Fallbacks
        signature = getattr(origin, "author_signature", None)
        if signature:
            return html.escape(str(signature))
    except Exception:
        pass
    return "Noma'lum"


async def log_forward_event(chat_id: int, user_id: int) -> None:
    ts = get_current_timestamp_utc()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO forward_events (chat_id, user_id, ts) VALUES (?, ?, ?)",
            (chat_id, user_id, ts),
        )
        await db.commit()


async def increment_forward_count(chat_id: int, user_id: int) -> int:
    today = get_today_date()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT count FROM forward_counts WHERE chat_id = ? AND user_id = ? AND date = ?",
            (chat_id, user_id, today),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            new_count = 1
            await db.execute(
                "INSERT INTO forward_counts (chat_id, user_id, date, count) VALUES (?, ?, ?, ?)",
                (chat_id, user_id, today, new_count),
            )
        else:
            new_count = int(row[0]) + 1
            await db.execute(
                "UPDATE forward_counts SET count = ? WHERE chat_id = ? AND user_id = ? AND date = ?",
                (new_count, chat_id, user_id, today),
            )
        await db.commit()
        return new_count


async def get_self_can_restrict(bot: Bot, chat_id: int) -> bool:
    me = await bot.get_me()
    member = await bot.get_chat_member(chat_id, me.id)
    status = getattr(member, "status", None)
    if status not in {"administrator", "creator"}:
        return False
    # For administrators, ensure can_restrict_members is True (creator always True)
    if status == "creator":
        return True
    return bool(getattr(member, "can_restrict_members", False))


async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, user_id)
    return getattr(member, "status", None) in {"administrator", "creator"}


async def apply_punishment(
    bot: Bot, chat_id: int, user_id: int, count: int
) -> Optional[str]:
    if count >= 4:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        return "ban"
    # Mute durations in minutes for 1..3
    durations = {1: 5, 2: 15, 3: 30}
    duration_min = durations.get(count, 30)
    until = datetime.now(timezone.utc) + timedelta(minutes=duration_min)
    permissions = ChatPermissions(
        can_send_messages=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
    )
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=permissions,
        until_date=until,
    )
    return f"mute_{duration_min}m"


@router.message(F.chat.type.in_({"group", "supergroup"}) & F.forward_origin)
async def on_forwarded_message(message: Message, bot: Bot) -> None:
    chat_id = message.chat.id
    from_user = message.from_user
    if from_user is None:
        # System message; just ignore
        return
    user_id = from_user.id

    # Try to delete forwarded message
    try:
        await message.delete()
    except Exception:
        # Ignore deletion errors (e.g., insufficient rights or already deleted)
        pass

    # Log per-violation timestamp to DB
    try:
        await log_forward_event(chat_id, user_id)
    except Exception:
        # Do not block flow on logging errors
        pass

    # Skip punishing admins/owner but still record count and delete
    is_admin = False
    try:
        is_admin = await is_user_admin(bot, chat_id, user_id)
    except Exception:
        is_admin = False

    # Increment and get user's forward count for this chat
    count = await increment_forward_count(chat_id, user_id)

    # Apply punishment only if bot can restrict and user is not admin
    if not is_admin:
        can_restrict = await get_self_can_restrict(bot, chat_id)
        if can_restrict:
            try:
                action = await apply_punishment(bot, chat_id, user_id, count)
                # Optionally notify the chat briefly (fail silently if no rights)
                if action is not None:
                    # Friendly, formatted notification with emojis and details
                    when_str = get_current_timestamp_local_ms()
                    display_name = html.escape(from_user.full_name)
                    user_anchor = f'<a href="tg://user?id={user_id}">{display_name}</a>'
                    src_html = format_forward_source_html(message)
                    # Humanized count text (e.g., 1-marta, 2-marta ...)
                    count_text = f"{count}-marotaba forward xabari yubordi!"
                    # Action pretty text
                    action_texts = {
                        "mute_5m": "🔇 Foydalanuvchi 5 daqiqa mute",
                        "mute_15m": "🔇 Foydalanuvchi 15 daqiqa mute",
                        "mute_30m": "🔇 Foydalanuvchi 30 daqiqa mute",
                        "ban": "🚷 Foydalanuvchi guruhdan chiqarildi",
                    }
                    action_pretty = action_texts.get(action, "")
                    notice = (
                        "<b>⚠️ Foydalanuvchi forward qilgan xabar o'chirildi!</b>\n"
                        f"👤 <b>Yuboruvchi:</b> {user_anchor}\n"
                        f"🔁 <b>Forward manbasi:</b> {src_html}\n"
                        f"⏰ <b>Vaqt:</b> {when_str}\n"
                        f"📊 <b>1-kun ichida:</b> {count_text}\n"
                        f"⚙️ <b>Chora:</b> {action_pretty}"
                    )
                    await bot.send_message(
                        chat_id,
                        notice,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
            except Exception:
                # Ignore restriction errors
                pass


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is not set")
    await init_db()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(
        bot, allowed_updates=["message", "chat_member", "my_chat_member"]
    )


if __name__ == "__main__":
    try:
        print(f"Bot started")
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"Bot stopped")
