from pyrogram import Client, filters
from pyrogram.types import Message

# শুধু এডমিনদের জন্য (ADMINS লিস্ট থেকে চেক করবে)
ADMINS = [7862181538]  # তুমি চাইলে এখানে তোমার আরো এডমিন আইডি যোগ করতে পারো

@Client.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_panel(_, message: Message):
    text = """
<b>ʜᴇʟᴘ: Aᴅᴍɪɴ Mᴏᴅᴜʟᴇs</b>

<b>Note:</b> This section is accessible only by <b>Bot Admins</b>.

━━━━━━━━━━━━━━━━━━

<b>📂 System Management:</b>
• <code>/logs</code> — View recent system errors.
• <code>/siam</code> — Check the file status in the database. (Anyone can use)
• <code>/delete</code> — Delete a specific file from the database.
• <code>/deletefiles</code> — Remove CamRip and PreDVD files.
• <code>/channel</code> — View the number of connected channels.
• <code>/leave</code> — Make the bot leave from a chat.

━━━━━━━━━━━━━━━━━━

<b>🤖 Post Management:</b>
• <code>/listtoday</code> — List today's uploaded Movies/Series.
• <code>/postlist</code> — Post all today's uploads to your channel.
• <code>/clear_today_list</code> — Clear today's movie/series data.

━━━━━━━━━━━━━━━━━━

<b>👥 User & Chat Management:</b>
• <code>/users</code> — View all registered users with IDs.
• <code>/chats</code> — View all connected chats/groups.
• <code>/disable</code> — Disable a chat/group.
• <code>/ban</code> — Ban a user.
• <code>/unban</code> — Unban a user.

━━━━━━━━━━━━━━━━━━

<b>📣 Broadcasting:</b>
• <code>/broadcast</code> — Send a message to all users.
• <code>/grp_broadcast</code> — Send a message to all groups.
• <code>/broadcast_user</code> — Send a custom message to a specific user.
  └ <i>Example:</i> <code>/broadcast_user 728727181</code> (Reply with message)

━━━━━━━━━━━━━━━━━━

<b>🔎 Global Filters:</b>
• <code>/gfilter</code> — Add a new global filter.
• <code>/gfilters</code> — View all global filters.
• <code>/delg</code> — Delete a specific global filter.
• <code>/delallg</code> — Delete all global filters at once.

━━━━━━━━━━━━━━━━━━

<b>🎬 Movie/Series Requests:</b>
• <code>/requestbot</code> — Request a Movie/Series. (Support group only)
• <code>/requestlist</code> — View pending requests.
• <code>/clearrequests</code> — Clear all pending requests.

━━━━━━━━━━━━━━━━━━

<b>⭐ Premium Management:</b>
• <code>/add_premium user_id time</code> — Add a premium user.
  └ <i>Example:</i> <code>/add_premium 5678985 1year</code>
• <code>/remove_premium user_id</code> — Remove a premium user.
  └ <i>Example:</i> <code>/remove_premium 67644577</code>

━━━━━━━━━━━━━━━━━━

<b>Tip:</b> Always use the correct command format to avoid errors!
"""
    await message.reply_text(text, quote=True)





# plugins/backdrop.py

# plugins/backdrop.py
