import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

@Client.on_message(filters.command(["song", "mp3"]) & filters.private)
async def song_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** /song song name")

    query = " ".join(message.command[1:])
    msg = await message.reply(f"🔍 Searching `{query}` on YouTube...")

    try:
        # Search for the song on YouTube
        results = YoutubeSearch(query, max_results=1).to_dict()
        video = results[0]
        url = f"https://youtube.com{video['url_suffix']}"
        title = video['title']
        thumbnail_url = video["thumbnails"][0]
    except Exception as e:
        return await msg.edit(f"❌ Search error: {e}")

    # Save the thumbnail
    thumb_name = f"thumb_{message.from_user.id}.jpg"
    with open(thumb_name, 'wb') as f:
        f.write(requests.get(thumbnail_url).content)

    await msg.edit("🎧 Downloading with yt-dlp + cookies...")

    # yt-dlp options for downloading the audio
    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best audio quality
        'outtmpl': f'{message.from_user.id}.mp3',  # Output file name based on user id
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'youtube_cookies.txt',  # Make sure your cookies file path is correct
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Convert to audio using FFmpeg
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # Set audio quality to 192 kbps
        }],
    }

    try:
        # Download the video using yt-dlp
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
    except Exception as e:
        return await msg.edit(f"❌ yt-dlp error: `{e}`")

    # Send the downloaded audio to the user
    await client.send_audio(
        chat_id=message.chat.id,
        audio=file_name,
        caption=f"🎵 **{title}**",
        performer="YouTube",
        title=title,
        thumb=thumb_name,
        reply_to_message_id=message.id
    )

    await msg.delete()

    # Clean up the temporary files
    for f in (file_name, thumb_name):
        if os.path.exists(f):
            os.remove(f)