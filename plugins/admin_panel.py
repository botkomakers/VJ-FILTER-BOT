from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from database.gfilters_mdb import clear_all_requests, get_all_requests
from helper.database import db
import traceback
import asyncio

admin_filter = filters.user(ADMINS)

@Client.on_message(filters.command("admin") & admin_filter)
async def admin_panel(_, message: Message):
    btn = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗒️ Logs", callback_data="logs"),
             InlineKeyboardButton("👥 Users", callback_data="users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
            [InlineKeyboardButton("❌ Clear Requests", callback_data="clearrequests")],
            [InlineKeyboardButton("🚫 Ban", callback_data="ban"),
             InlineKeyboardButton("✅ Unban", callback_data="unban")],
        ]
    )
    await message.reply("**Welcome to Admin Panel**", reply_markup=btn)

@Client.on_callback_query(filters.regex("logs") & admin_filter)
async def logs_cb(_, query):
    try:
        with open("logs.txt", "rb") as f:
            await query.message.reply_document(f, caption="Here are the recent logs.")
    except Exception as e:
        await query.message.reply(f"Error:\n`{e}`")
    await query.answer()

@Client.on_callback_query(filters.regex("users") & admin_filter)
async def users_cb(_, query):
    users = await db.total_users_count()
    await query.message.reply(f"**Total Users:** `{users}`")
    await query.answer()

@Client.on_callback_query(filters.regex("clearrequests") & admin_filter)
async def clear_requests_cb(_, query):
    await clear_all_requests()
    await query.message.reply("✅ All movie requests cleared from the database.")
    await query.answer()

@Client.on_callback_query(filters.regex("broadcast") & admin_filter)
async def broadcast_cb(_, query):
    await query.message.reply("Please send the broadcast message (Text/Media).")
    await query.answer()

@Client.on_message(filters.reply & admin_filter)
async def broadcast_start(client, message):
    if not message.reply_to_message:
        return
    total, success, failed = 0, 0, 0
    text = message.reply_to_message.text or message.reply_to_message.caption
    users = await db.get_all_users()
    for user in users:
        try:
            await client.copy_message(
                chat_id=user["id"],
                from_chat_id=message.reply_to_message.chat.id,
                message_id=message.reply_to_message.id
            )
            success += 1
        except Exception:
            failed += 1
        total += 1
        await asyncio.sleep(0.3)
    await message.reply(f"**Broadcast Completed**\n\nTotal: {total}\nSuccess: {success}\nFailed: {failed}")

@Client.on_message(filters.command("ban") & admin_filter)
async def ban_user(_, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/ban user_id`", quote=True)
    user_id = int(message.command[1])
    await db.ban_user(user_id)
    await message.reply(f"User `{user_id}` has been banned.")

@Client.on_message(filters.command("unban") & admin_filter)
async def unban_user(_, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/unban user_id`", quote=True)
    user_id = int(message.command[1])
    await db.unban_user(user_id)
    await message.reply(f"User `{user_id}` has been unbanned.")

@Client.on_message(filters.command("clearrequests") & admin_filter)
async def clear_requests(_, message):
    await clear_all_requests()
    await message.reply("✅ All movie requests cleared.")

@Client.on_message(filters.command("requestlist") & admin_filter)
async def request_list(_, message):
    requests = await get_all_requests()
    if not requests:
        return await message.reply("❌ No pending requests.")
    msg = "**Pending Movie Requests:**\n\n"
    for req in requests:
        msg += f"➤ {req['movie_name']} — `{req['user_id']}`\n"
    await message.reply(msg)