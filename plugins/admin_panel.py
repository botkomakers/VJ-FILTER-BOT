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

# plugins/backdrop.py

import random
import aiohttp
from pyrogram import Client, filters

from info import TMDB_API_KEY  # Ensure this exists!

@Client.on_message(filters.command("backdrop"))
async def random_backdrop(client, message):
    await message.reply_chat_action("upload_photo")
    try:
        async with aiohttp.ClientSession() as session:
            # Randomly decide between 'movie' or 'tv'
            category = random.choice(["movie", "tv"])
            
            # Get a random page (1-500)
            page = random.randint(1, 500)
            
            url = f"https://api.themoviedb.org/3/discover/{category}?api_key={TMDB_API_KEY}&page={page}&language=en-US"
            async with session.get(url) as resp:
                data = await resp.json()

            results = data.get("results")
            if not results:
                await message.reply_text("কিছুই পাইনি। আবার চেষ্টা করো।")
                return

            random_result = random.choice(results)
            backdrop_path = random_result.get("backdrop_path")

            if not backdrop_path:
                await message.reply_text("ব্যাকড্রপ ইমেজ পাইনি। আবার চেষ্টা করো।")
                return

            full_backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"

            title = random_result.get("title") or random_result.get("name") or "Unknown Title"
            overview = random_result.get("overview", "কোনো ডেসক্রিপশন নেই।")

            caption = f"**{title}**\n\n{overview}"

            await message.reply_photo(full_backdrop_url, caption=caption)

    except Exception as e:
        await message.reply_text(f"Error: {e}")