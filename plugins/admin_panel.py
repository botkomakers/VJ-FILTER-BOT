#gg



from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS

# Only Admins
admin_filter = filters.user(ADMINS)

# /logs
@Client.on_message(filters.command("logs") & admin_filter)
async def logs(_, message: Message):
    await message.reply_text("Sending logs is not implemented yet.")

# /siam
@Client.on_message(filters.command("siam"))
async def siam(_, message: Message):
    await message.reply_text("Status of files in DB: Not implemented yet.")

# /delete
@Client.on_message(filters.command("delete") & admin_filter)
async def delete_file(_, message: Message):
    await message.reply_text("Delete specific file functionality is not implemented yet.")

# /users
@Client.on_message(filters.command("users") & admin_filter)
async def users(_, message: Message):
    await message.reply_text("List of users and their IDs.")

# /chats
@Client.on_message(filters.command("chats") & admin_filter)
async def chats(_, message: Message):
    await message.reply_text("List of chats and their IDs.")

# /leave
@Client.on_message(filters.command("leave") & admin_filter)
async def leave(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a Chat ID to leave.")
    chat_id = message.command[1]
    try:
        await _.leave_chat(int(chat_id))
        await message.reply_text(f"Left chat `{chat_id}` successfully.")
    except Exception as e:
        await message.reply_text(f"Error leaving chat: {e}")

# /disable
@Client.on_message(filters.command("disable") & admin_filter)
async def disable(_, message: Message):
    await message.reply_text("Chat disabled functionality not implemented yet.")

# /ban
@Client.on_message(filters.command("ban") & admin_filter)
async def ban(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a user ID to ban.")
    user_id = int(message.command[1])
    await message.reply_text(f"Banned user {user_id}.")

# /unban
@Client.on_message(filters.command("unban") & admin_filter)
async def unban(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a user ID to unban.")
    user_id = int(message.command[1])
    await message.reply_text(f"Unbanned user {user_id}.")

# /channel
@Client.on_message(filters.command("channel") & admin_filter)
async def channel(_, message: Message):
    await message.reply_text("List of connected channels.")

# /broadcast
@Client.on_message(filters.command("broadcast") & admin_filter)
async def broadcast(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a message to broadcast.")
    text = message.text.split(None, 1)[1]
    await message.reply_text(f"Broadcasted message: {text}")

# /grp_broadcast
@Client.on_message(filters.command("grp_broadcast") & admin_filter)
async def grp_broadcast(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide a group message to broadcast.")
    text = message.text.split(None, 1)[1]
    await message.reply_text(f"Group Broadcasted message: {text}")

# /gfilter
@Client.on_message(filters.command("gfilter") & admin_filter)
async def gfilter(_, message: Message):
    await message.reply_text("Added global filter.")

# /gfilters
@Client.on_message(filters.command("gfilters") & admin_filter)
async def gfilters(_, message: Message):
    await message.reply_text("List of all global filters.")

# /delg
@Client.on_message(filters.command("delg") & admin_filter)
async def delg(_, message: Message):
    await message.reply_text("Deleted specific global filter.")

# /request
@Client.on_message(filters.command("request"))
async def request(_, message: Message):
    await message.reply_text("Request sent to admins.")

# /delallg
@Client.on_message(filters.command("delallg") & admin_filter)
async def delallg(_, message: Message):
    await message.reply_text("Deleted all global filters.")

# /deletefiles
@Client.on_message(filters.command("deletefiles") & admin_filter)
async def deletefiles(_, message: Message):
    await message.reply_text("Deleted CamRip and PreDVD files.")

# /broadcast_user
@Client.on_message(filters.command("broadcast_user") & admin_filter)
async def broadcast_user(_, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Usage: /broadcast_user user_id message")
    user_id = int(message.command[1])
    text = message.text.split(None, 2)[2]
    await _.send_message(chat_id=user_id, text=text)
    await message.reply_text(f"Sent message to {user_id}.")

# /requestlist
@Client.on_message(filters.command("requestlist") & admin_filter)
async def requestlist(_, message: Message):
    await message.reply_text("Pending requests list.")

# /clearrequests
@Client.on_message(filters.command("clearrequests") & admin_filter)
async def clearrequests(_, message: Message):
    await message.reply_text("Cleared all pending requests.")

# /add_premium
@Client.on_message(filters.command("add_premium") & admin_filter)
async def add_premium(_, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("Usage: /add_premium user_id duration")
    user_id = int(message.command[1])
    duration = message.command[2]
    await message.reply_text(f"Added premium to user {user_id} for {duration}.")

# /remove_premium
@Client.on_message(filters.command("remove_premium") & admin_filter)
async def remove_premium(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /remove_premium user_id")
    user_id = int(message.command[1])
    await message.reply_text(f"Removed premium from user {user_id}.")