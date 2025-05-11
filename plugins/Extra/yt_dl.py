from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
import requests, os

@Client.on_message(filters.command("song") & filters.private)
async def song_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("**Usage:** `/song গান নাম`")

    status_msg = await message.reply(f"🔎 Searching for **{query}**...")

    try:
        from youtube_search import YoutubeSearch
        results = YoutubeSearch(query, max_results=1).to_dict()
        video = results[0]
        url = f"https://www.youtube.com{video['url_suffix']}"
        title = video['title']
        duration = video['duration']
        thumbnail_url = video['thumbnails'][0]
    except Exception as e:
        await status_msg.edit("❌ গান খুঁজে পাওয়া যায়নি।")
        return

    await status_msg.edit("⏬ Downloading audio...")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "outtmpl": f"{title}.%(ext)s",
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        await status_msg.edit("❌ ডাউনলোডে সমস্যা হয়েছে।")
        print(e)
        return

    # Download thumbnail
    thumb_file = f"{title}.jpg"
    with open(thumb_file, "wb") as f:
        f.write(requests.get(thumbnail_url).content)

    # Calculate duration in seconds
    duration_sec = 0
    try:
        parts = duration.split(":")
        for i in range(len(parts)):
            duration_sec += int(parts[-(i+1)]) * (60**i)
    except:
        duration_sec = None

    await message.reply_audio(
        audio=filename,
        title=title,
        performer="YouTube",
        caption=f"🎵 {title}",
        duration=duration_sec,
        thumb=thumb_file
    )

    await status_msg.delete()

    # Cleanup
    try:
        os.remove(filename)
        os.remove(thumb_file)
    except:
        pass