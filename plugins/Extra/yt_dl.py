from __future__ import unicode_literals

import os, asyncio, requests, re
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from info import CHNL_LNK  # Channel link for caption

def clean_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/song song name here`")

    query = " ".join(message.command[1:])
    user = message.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    
    status_msg = await message.reply(f"**🎵 Searching your song:** `{query}`")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await status_msg.edit("❌ No results found. Try another song.")

        song_data = results[0]
        video_url = f"https://youtube.com{song_data['url_suffix']}"
        title = clean_filename(song_data["title"][:40])
        thumbnail_url = song_data["thumbnails"][0]
        duration_str = song_data["duration"]
        performer = "NETWORKS™"

        # Download thumbnail
        thumb_path = f"{title}_thumb.jpg"
        with open(thumb_path, 'wb') as f:
            f.write(requests.get(thumbnail_url).content)

    except Exception as e:
        return await status_msg.edit(f"⚠️ Failed to search song.\n`{str(e)}`")

    await status_msg.edit("**⬇️ Downloading your song...**")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "outtmpl": f"{title}.m4a",
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            audio_file = ydl.prepare_filename(info)
    except Exception as e:
        return await status_msg.edit(f"❌ Download failed.\n`{str(e)}`")

    # Convert duration string (e.g. "3:45") to seconds
    duration_parts = duration_str.split(":")
    duration_sec = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration_parts)))

    caption = f"**BY›› [UPDATE]({CHNL_LNK})**"

    try:
        await message.reply_audio(
            audio=audio_file,
            caption=caption,
            title=title,
            performer=performer,
            duration=duration_sec,
            thumb=thumb_path
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit(f"❌ Failed to send audio.\n`{str(e)}`")

    # Clean up
    for file in [audio_file, thumb_path]:
        if os.path.exists(file):
            os.remove(file)