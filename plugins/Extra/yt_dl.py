import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]

def download_thumbnail(url: str, filename: str):
    try:
        r = requests.get(url)
        if r.ok:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return filename
    except Exception as e:
        print(f"Thumbnail error: {e}")
    return None

async def progress_hook(d, msg, last_time):
    if d['status'] == 'downloading':
        now = time.time()
        if now - last_time[0] > 2:
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '0 KB/s')
            eta = d.get('eta', 0)
            text = f"⬇️ Downloading...\nProgress: {percent}\nSpeed: {speed}\nETA: {eta}s"
            try:
                await msg.edit(text)
                last_time[0] = now
            except:
                pass

@Client.on_message(filters.command("video") & filters.private)
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /video [ভিডিও নাম]")

    status = await message.reply(f"🔍 Searching for `{query}`...")

    try:
        result = YoutubeSearch(query, max_results=1).to_dict()[0]
    except:
        return await status.edit("❌ No video found.")

    url = f"https://www.youtube.com{result['url_suffix']}"
    title = result['title']
    duration = result['duration']
    thumb_url = result['thumbnails'][0]

    file_name = sanitize_filename(title) + ".mp4"
    thumb_file = sanitize_filename(title) + ".jpg"
    last_time = [time.time()]

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": file_name,
        "cookiefile": "youtube_cookies.txt",
        "progress_hooks": [lambda d: client.loop.create_task(progress_hook(d, status, last_time))],
        "quiet": True,
        "no_warnings": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        await status.edit("❌ ভিডিও ডাউনলোডে সমস্যা হয়েছে।")
        print(e)
        return

    download_thumbnail(thumb_url, thumb_file)

    async def upload_progress(current, total):
        percent = f"{(current / total) * 100:.1f}%"
        try:
            await status.edit(f"⬆️ Uploading...\nProgress: {percent}")
        except:
            pass

    try:
        await message.reply_video(
            video=file_name,
            caption=f"🎬 Title: {title}\n⏱️ Duration: {duration}",
            thumb=thumb_file if os.path.exists(thumb_file) else None,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("▶️ Watch on YouTube", url=url)
            ]]),
            progress=upload_progress
        )
    except Exception as e:
        await message.reply("❌ ভিডিও পাঠাতে সমস্যা হয়েছে।")
        print(e)

    await status.delete()
    for f in [file_name, thumb_file]:
        if os.path.exists(f):
            os.remove(f)