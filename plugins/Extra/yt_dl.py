import requests, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

API_URL = "https://loader.to/ajax/download.php"

@Client.on_message(filters.command(["song", "mp3"]) & filters.private)
async def fetch_song(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/song song name`")

    query = " ".join(message.command[1:])
    status = await message.reply(f"🔍 Searching for: `{query}`")

    # Step 1: Search on YouTube (using youtube_search)
    from youtube_search import YoutubeSearch
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await status.edit("❌ No results found.")
        video = results[0]
        title = video["title"]
        video_url = f"https://youtube.com{video['url_suffix']}"
    except Exception as e:
        return await status.edit(f"❌ Search failed: {e}")

    await status.edit("⏳ Sending download request to loader.to...")

    # Step 2: Send request to loader.to API
    try:
        payload = {
            "q": video_url,
            "f": "mp3",
            "start": "0",
            "end": "0"
        }
        res = requests.post(API_URL, data=payload).json()

        if res.get("download_url"):
            download_url = res["download_url"]
        else:
            return await status.edit("⚠️ Unable to get download URL. Try another song.")
    except Exception as e:
        return await status.edit(f"❌ API failed: {e}")

    await status.edit("📥 Downloading and sending the audio...")

    try:
        await client.send_audio(
            chat_id=message.chat.id,
            audio=download_url,
            title=title,
            caption=f"🎵 **{title}**\n📥 From: loader.to",
            reply_to_message_id=message.id
        )
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Failed to send audio: {e}")