#make by siam

#requestbot

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.gfilters_mdb import add_movie_request, delete_movie_request, get_all_requests, clear_all_requests

LOG_CHANNEL = -1002589776901
ADMIN_ID = 7862181538

@Client.on_message(filters.command("requestbot") & filters.private)
async def handle_request(client, message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/requestbot Movie Name`", quote=True)

    movie_name = " ".join(message.command[1:])
    user = message.from_user

    await add_movie_request(user.id, movie_name)

    # Notify admins
    await send_movie_request_to_admins(client, movie_name, user.id, user.first_name, LOG_CHANNEL)
    await send_movie_request_to_admins(client, movie_name, user.id, user.first_name, ADMIN_ID)

    await message.reply(
        f"✅ **Your request for** `{movie_name}` **has been submitted successfully!**\n"
        "You'll be notified once it's available.",
        quote=True
    )

@Client.on_callback_query(filters.regex(r"^(uploaded|uploading|cantupload)_\d+\|.+$"))
async def handle_request_action(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    action, rest = data.split("_", 1)
    user_id_str, movie_name = rest.split("|", 1)

    try:
        user_id = int(user_id_str)
    except ValueError:
        return await callback_query.answer("❌ Invalid user ID!", show_alert=True)

    if action == "uploaded":
        reply_text = f"✅ The movie **{movie_name}** is already available in our collection!"
    elif action == "uploading":
        reply_text = f"⏳ The movie **{movie_name}** will be uploaded shortly. Please stay tuned!"
    elif action == "cantupload":
        reply_text = f"❌ Sorry! The movie **{movie_name}** could not be uploaded."
    else:
        reply_text = "❌ Unknown action!"

    try:
        await client.send_message(chat_id=user_id, text=reply_text)
    except Exception as e:
        await callback_query.answer("❌ Failed to send message to the user.", show_alert=True)
        print(f"[Error] Couldn't send message to {user_id}: {e}")
        return

    await callback_query.answer("✅ Response sent to the user.")

    try:
        await callback_query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await delete_movie_request(movie_name)

@Client.on_message(filters.command("requestlist") & filters.user(ADMIN_ID))
async def request_list(client, message):
    data = await get_all_requests()
    if not data:
        return await message.reply("📭 No pending movie requests.")

    text = "🎞️ **Pending Movie Requests:**\n\n"
    for i, req in enumerate(data, start=1):
        text += f"{i}. `{req['movie_name']}` - [User](tg://user?id={req['user_id']})\n"

    await message.reply(text)

@Client.on_message(filters.command("clearrequests") & filters.user(ADMIN_ID))
async def clear_requests(client, message):
    await clear_all_requests()
    await message.reply("✅ All pending requests have been cleared.")

async def send_movie_request_to_admins(client: Client, movie_name: str, user_id: int, user_name: str, chat_id: int):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Already Available", callback_data=f"uploaded_{user_id}|{movie_name}"),
            InlineKeyboardButton("⏳ Uploading Soon", callback_data=f"uploading_{user_id}|{movie_name}"),
            InlineKeyboardButton("🚫 Can't Upload", callback_data=f"cantupload_{user_id}|{movie_name}")
        ]
    ])

    text = (
        f"📩 **New Movie Request Received**\n\n"
        f"🎬 **Movie:** `{movie_name}`\n"
        f"👤 **Requested by:** [{user_name}](tg://user?id={user_id})"
    )

    await client.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )