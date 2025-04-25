from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import ADMINS
from database.gfilters_mdb import clear_all_requests, get_all_requests
import asyncio

admin_filter = filters.user(ADMINS)

@Client.on_message(filters.command("admin") & admin_filter)
async def admin_panel(_, message: Message):
    btn = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗒️ Logs", callback_data="logs"),
             InlineKeyboardButton("👥 Users", callback_data="users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
             InlineKeyboardButton("📄 Requests", callback_data="requests")],
            [InlineKeyboardButton("❌ Clear Requests", callback_data="clearrequests")],
            [InlineKeyboardButton("🚫 Ban", callback_data="ban_user"),
             InlineKeyboardButton("✅ Unban", callback_data="unban_user")],
            [InlineKeyboardButton("⭐ Add Premium", callback_data="add_premium"),
             InlineKeyboardButton("⚠️ Remove Premium", callback_data="remove_premium")],
        ]
    )
    await message.reply("**Welcome to Admin Panel**", reply_markup=btn)

@Client.on_callback_query(admin_filter)
async def admin_callbacks(client, query: CallbackQuery):
    data = query.data
    uid = query.from_user.id

    if data == "logs":
        try:
            with open("logs.txt", "rb") as f:
                await query.message.reply_document(f, caption="Here are the recent logs.")
        except Exception as e:
            await query.message.reply(f"Error:\n`{e}`")

    elif data == "users":
        users = await db.total_users_count()
        await query.message.reply(f"**Total Users:** `{users}`")

    elif data == "clearrequests":
        await clear_all_requests()
        await query.message.reply("✅ All movie requests cleared from the database.")

    elif data == "requests":
        requests = await get_all_requests()
        if not requests:
            await query.message.reply("❌ No pending requests.")
        else:
            msg = "**Pending Movie Requests:**\n\n"
            for req in requests:
                msg += f"➤ {req['movie_name']} — `{req['user_id']}`\n"
            await query.message.reply(msg)

    elif data == "broadcast":
        await query.message.reply("Please send the broadcast message (Text/Media) **as a reply to this message**.")
        client.broadcast_trigger = uid

    elif data == "ban_user":
        await query.message.reply("Send user ID to **ban**, as reply to this message.")
        client.ban_trigger = uid

    elif data == "unban_user":
        await query.message.reply("Send user ID to **unban**, as reply to this message.")
        client.unban_trigger = uid

    elif data == "add_premium":
        await query.message.reply("Send user ID to **add as premium**, as reply to this message.")
        client.add_premium_trigger = uid

    elif data == "remove_premium":
        await query.message.reply("Send user ID to **remove from premium**, as reply to this message.")
        client.remove_premium_trigger = uid

    await query.answer()

@Client.on_message(admin_filter & filters.reply)
async def handle_admin_replies(client, message: Message):
    reply_text = message.text.strip()
    uid = message.from_user.id

    if getattr(client, "broadcast_trigger", None) == uid:
        total, success, failed = 0, 0, 0
        users = await db.get_all_users()
        for user in users:
            try:
                await client.copy_message(
                    chat_id=user["id"],
                    from_chat_id=message.chat.id,
                    message_id=message.id
                )
                success += 1
            except:
                failed += 1
            total += 1
            await asyncio.sleep(0.3)
        await message.reply(f"**Broadcast Completed**\n\nTotal: {total}\nSuccess: {success}\nFailed: {failed}")
        client.broadcast_trigger = None

    elif getattr(client, "ban_trigger", None) == uid:
        try:
            user_id = int(reply_text)
            await db.ban_user(user_id)
            await message.reply(f"🚫 User `{user_id}` has been banned.")
        except:
            await message.reply("Invalid ID!")
        client.ban_trigger = None

    elif getattr(client, "unban_trigger", None) == uid:
        try:
            user_id = int(reply_text)
            await db.unban_user(user_id)
            await message.reply(f"✅ User `{user_id}` has been unbanned.")
        except:
            await message.reply("Invalid ID!")
        client.unban_trigger = None

    elif getattr(client, "add_premium_trigger", None) == uid:
        try:
            user_id = int(reply_text)
            await db.add_premium_user(user_id)
            await message.reply(f"⭐ User `{user_id}` has been added to Premium.")
        except:
            await message.reply("Invalid ID!")
        client.add_premium_trigger = None

    elif getattr(client, "remove_premium_trigger", None) == uid:
        try:
            user_id = int(reply_text)
            await db.remove_premium_user(user_id)
            await message.reply(f"⚠️ User `{user_id}` has been removed from Premium.")
        except:
            await message.reply("Invalid ID!")
        client.remove_premium_trigger = None