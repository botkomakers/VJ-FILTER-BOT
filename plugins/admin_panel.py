from pyrogram import Client, filters
from pyrogram.types import Message

# শুধু এডমিনদের জন্য (ADMINS লিস্ট থেকে চেক করবে)
ADMINS = [7862181538]  # তুমি চাইলে এখানে তোমার আরো এডমিন আইডি যোগ করতে পারো

@Client.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_panel(_, message: Message):
    text = """ʜᴇʟᴘ: Aᴅᴍɪɴ Mᴏᴅs

Note: This module is only available for Bot Admins.

━━━━━━━━━━━━━━━━━━

Commands & Usage:

📂 System Management:
• /logs — Get the recent errors.
• /siam — Get the status of files in the database. (Anyone can use)
• /delete — Delete a specific file from the database.
• /deletefiles — Delete CamRip and PreDVD files from the database.
• /channel — View the total number of connected channels.
• /leave — Leave from a chat.

👥 User & Chat Management:
• /users — Get the list of all users and their IDs.
• /chats — Get the list of all chats and their IDs.
• /disable — Disable a chat.
• /ban — Ban a user.
• /unban — Unban a user.

📣 Broadcasting:
• /broadcast — Broadcast a message to all users.
• /grp_broadcast — Broadcast a message to all connected groups.
• /broadcast_user — Broadcast a message to a specific user by user ID.

🔎 Global Filters:
• /gfilter — Add a global filter.
• /gfilters — View all global filters.
• /delg — Delete a specific global filter.
• /delallg — Delete all global filters.

🎬 Requests:
• /request — Request a Movie/Series. (Support group only | Anyone can use)
• /requestlist — View pending requests.
• /clearrequests — Clear all pending requests.

⭐ Premium Management:
• /add_premium user_id time — Add a premium user.
  Example: /add_premium 5678985 1year
• /remove_premium user_id — Remove a premium user.
  Example: /remove_premium 67644577

━━━━━━━━━━━━━━━━━━

Tip: Always use the correct format for commands to avoid errors.
"""
    await message.reply_text(text, quote=True)





# plugins/backdrop.py

import random
import aiohttp
from pyrogram import Client, filters
from info import TMDB_API_KEY  # তোমার info.py তে TMDB_API_KEY রাখতে হবে

TMDB_API_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

@Client.on_message(filters.command("backdrop") & filters.private)
async def send_random_backdrop(client, message):
    await message.reply_chat_action("upload_photo")
    try:
        media_type = random.choice(["movie", "tv"])
        page = random.randint(1, 100)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{TMDB_API_URL}/discover/{media_type}",
                params={
                    "api_key": TMDB_API_KEY,
                    "language": "en-US",
                    "sort_by": "popularity.desc",
                    "page": page,
                }
            ) as resp:
                if resp.status != 200:
                    await message.reply_text("TMDB সার্ভার থেকে ডেটা আনা যাচ্ছে না...")
                    return
                data = await resp.json()

        results = data.get("results")
        if not results:
            await message.reply_text("কোনো রেজাল্ট পাওয়া যায়নি!")
            return

        random_result = random.choice(results)
        backdrop_path = random_result.get("backdrop_path")

        if not backdrop_path:
            await message.reply_text("ব্যাকড্রপ ইমেজ খুঁজে পাওয়া যায়নি!")
            return

        title = random_result.get("title") or random_result.get("name") or "Unknown Title"
        overview = random_result.get("overview") or "No description available."

        await message.reply_photo(
            photo=f"{IMAGE_BASE_URL}{backdrop_path}",
            caption=f"**{title}**\n\n{overview}",
        )

    except Exception as e:
        await message.reply_text(f"ভুল হয়েছে:\n`{e}`")