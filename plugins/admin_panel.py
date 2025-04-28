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

🤖 Post Channel 
• /listtoday - Get all today uploaded movie or series.
• /postlist - Post today uploaded all movie or series in channel.
• /clear_today_list - Clear all movie today data.

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
• /requestbot — Request a Movie/Series. (Support group only | Anyone can use)
• /requestlist — View pending requests.
• /clearrequests — Clear all pending request

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
