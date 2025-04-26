from pyrogram import Client, filters
from pyrogram.types import Message

# শুধু এডমিনদের জন্য (ADMINS লিস্ট থেকে চেক করবে)
ADMINS = [7862181538]  # তুমি চাইলে এখানে তোমার আরো এডমিন আইডি যোগ করতে পারো

@Client.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_panel(_, message: Message):
    text = """
<b>ʜᴇʟᴘ: Aᴅᴍɪɴ Mᴏᴅs</b>

<b>Note:</b> This module only works for my Admins.

<b>Commands and Usage:</b>

• <code>/logs</code> - Get the recent errors.  
• <code>/siam</code> - Get the status of files in DB. [Anyone can use]  
• <code>/delete</code> - Delete a specific file from the database.  
• <code>/users</code> - Get the list of users and their IDs.  
• <code>/chats</code> - Get the list of chats and their IDs.  
• <code>/leave</code> - Leave from a chat.  
• <code>/disable</code> - Disable a chat.  
• <code>/ban</code> - Ban a user.  
• <code>/unban</code> - Unban a user.  
• <code>/channel</code> - Get the list of total connected channels.  
• <code>/broadcast</code> - Broadcast a message to all users.  
• <code>/grp_broadcast</code> - Broadcast a message to all connected groups.  
• <code>/gfilter</code> - Add a global filter.  
• <code>/gfilters</code> - View the list of all global filters.  
• <code>/delg</code> - Delete a specific global filter.  
• <code>/delallg</code> - Delete all global filters from the bot's database.  
• <code>/request</code> - Send a Movie/Series request to Bot Admins. [Support group only | Anyone can use]  
• <code>/deletefiles</code> - Delete CamRip and PreDVD files from the database.  
• <code>/broadcast_user</code> - Broadcast message to a specific user by user ID.  
• <code>/requestlist</code> - View pending movie/series requests made by users.  
• <code>/clearrequests</code> - Clear all pending requests.  
• <code>/add_premium</code> - Add a premium user. Usage: /add_premium user_id time (Example: /add_premium 5678985 1year)  
• <code>/remove_premium</code> - Remove a premium user. Usage: /remove_premium user_id (Example: /remove_premium 67644577)
"""
    await message.reply_text(text, quote=True)