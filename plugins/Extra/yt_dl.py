import requests
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command(["song", "mp3"]) & filters.private)
async def song_download(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** /song song name")

    query = " ".join(message.command[1:])
    status = await message.reply(f"🔍 Searching `{query}` on YouTube...")

    try:
        # Step 1: Search on YouTube
        from youtube_search import YoutubeSearch
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await status.edit("❌ No results found.")

        video = results[0]
        title = video["title"]
        video_url = f"https://youtube.com{video['url_suffix']}"
    except Exception as e:
        return await status.edit(f"❌ Search failed: {e}")

    await status.edit("🔗 Fetching MP3 link...")

    try:
        # Step 2: Call yt-api.com for mp3 download link
        api_url = f"https://yt-api.com/api/button/mp3?url={video_url}"
        res = requests.get(api_url).json()
        buttons = res.get("buttons")

        if not buttons:
            return await status.edit("❌ Couldn't get the download link.")

        # Pick the first available MP3 download link
        mp3_url = buttons[0]["url"]
    except Exception as e:
        return await status.edit(f"❌ API error: {e}")

    await status.edit("📤 Sending audio...")

    try:
        await client.send_audio(
            chat_id=message.chat.id,
            audio=mp3_url,
            caption=f"🎵 **{title}**\n📥 via yt-api.com",
            title=title,
            performer="YouTube",
            reply_to_message_id=message.id
        )
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Failed to send audio: {e}")