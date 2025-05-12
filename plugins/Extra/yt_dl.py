import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

# -------------------- ফাইলনেম সেনিটাইজ --------------------
def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]

# -------------------- থাম্বনেইল ডাউনলোড --------------------
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

# -------------------- প্রগ্রেস হুক --------------------
async def progress_hook(d, msg, last_time):
    if d['status'] == 'downloading':
        now = time.time()
        if now - last_time[0] > 2:
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '0 KB/s')
            eta = d.get('eta', 0)
            # প্রগ্রেস বার স্টাইলিং
            progress_bar = "█" * int(d['downloaded_bytes'] / d['total_bytes'] * 20)  # বার ২০ ইউনিটে ভাগ
            progress_text = f"⬇️ Downloading...\n[{progress_bar:<20}] {percent}\nSpeed: {speed}\nETA: {eta}s"
            try:
                await msg.edit(progress_text)
                last_time[0] = now
            except:
                pass

# -------------------- /song হ্যান্ডলার --------------------
@Client.on_message(filters.command("song") & filters.private)
async def song_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /song [গানের নাম]")

    status = await message.reply(f"🔍 Searching for `{query}`...")

    try:
        result = YoutubeSearch(query, max_results=1).to_dict()[0]
    except:
        return await status.edit("❌ No song found.")

    url = f"https://www.youtube.com{result['url_suffix']}"
    title = result['title']
    duration = result['duration']
    thumb_url = result['thumbnails'][0]

    file_name = sanitize_filename(title) + ".mp3"
    thumb_file = sanitize_filename(title) + ".jpg"
    last_time = [time.time()]

    # ইউটিউব থেকে অডিও ডাউনলোড করার জন্য অপশন
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
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
        await status.edit("❌ গানের ডাউনলোডে সমস্যা হয়েছে।")
        print(e)
        return

    download_thumbnail(thumb_url, thumb_file)

    # -------------------- আপলোড প্রগ্রেস --------------------
    async def upload_progress(current, total):
        percent = f"{(current / total) * 100:.1f}%"
        # আপলোড প্রগ্রেস বার স্টাইল
        upload_bar = "█" * int(current / total * 20)  # বার ২০ ইউনিটে ভাগ
        try:
            await status.edit(f"⬆️ Uploading...\n[{upload_bar:<20}] {percent}")
        except:
            pass

    # -------------------- গানের ফাইল আপলোড --------------------
    try:
        await message.reply_audio(
            audio=file_name,
            caption=f"🎶 Title: {title}\n⏱️ Duration: {duration}",
            thumb=thumb_file if os.path.exists(thumb_file) else None,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("▶️ Listen on YouTube", url=url)
            ]]),
            progress=upload_progress
        )
    except Exception as e:
        await message.reply("❌ গান পাঠাতে সমস্যা হয়েছে।")
        print(e)

    await status.delete()

    # -------------------- ফাইল ডিলিট --------------------
    for f in [file_name, thumb_file]:
        if os.path.exists(f):
            os.remove(f)

# -------------------- /video হ্যান্ডলার --------------------
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

    # -------------------- আপলোড প্রগ্রেস --------------------
    async def upload_progress(current, total):
        percent = f"{(current / total) * 100:.1f}%"
        upload_bar = "█" * int(current / total * 20)
        try:
            await status.edit(f"⬆️ Uploading...\n[{upload_bar:<20}] {percent}")
        except:
            pass

    # -------------------- ভিডিও ফাইল আপলোড --------------------
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

    # -------------------- ফাইল ডিলিট --------------------
    for f in [file_name, thumb_file]:
        if os.path.exists(f):
            os.remove(f)