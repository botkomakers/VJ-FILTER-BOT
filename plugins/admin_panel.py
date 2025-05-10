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


from pyrogram import Client, filters
from pyrogram.types import Message
from info import Info
import aiohttp

# JioSaavn Song Search Function
async def get_song(query):
    api = f"https://saavn.dev/api/search/songs?query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            data = await resp.json()
            if not data.get("data") or not data["data"]["results"]:
                return None
            first = data["data"]["results"][0]
            return {
                "title": first["name"],
                "artist": ", ".join([a["name"] for a in first["primaryArtists"]]),
                "media_url": first["downloadUrl"][-1]["link"],
                "image": first["image"][2]["link"]
            }

# Command: /song <name>
@Client.on_message(filters.command("song"))
async def song_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/song song name`", quote=True)

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Searching for your song...")

    try:
        song = await get_song(query)
        if not song:
            return await msg.edit("❌ No song found!")

        await client.send_audio(
            chat_id=message.chat.id,
            audio=song["media_url"],
            title=song["title"],
            performer=song["artist"],
            thumb=song["image"]
        )
        await msg.delete()
    except Exception as e:
        await msg.edit(f"❌ Error:\n`{e}`")