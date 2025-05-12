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
        response = requests.get(url)
        if response.ok:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"Error downloading thumbnail: {e}")
    return None

# -------------------- ডাউনলোড প্রগ্রেস হ্যান্ডলিং --------------------
async def progress_hook(d, msg, last_time):
    if d['status'] == 'downloading':
        now = time.time()
        if now - last_time[0] > 2:  # Update every 2 seconds
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '0 KB/s')
            eta = d.get('eta', 0)
            eta_text = time.strftime('%M:%S', time.gmtime(eta)) if eta else "N/A"
            text = f"⬇️ Downloading...\nProgress: {percent}\nSpeed: {speed}\nETA: {eta_text}"
            try:
                await msg.edit(text)
                last_time[0] = now
            except Exception as e:
                print("Progress error:", e)

# -------------------- /video হ্যান্ডলার --------------------
@Client.on_message(filters.command("video") & filters.private)
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /video [ভিডিও নাম]")

    status = await message.reply(f"🔍 Searching YouTube for `{query}`...")

    try:
        result = YoutubeSearch(query, max_results=1).to_dict()[0]
    except Exception as e:
        await status.edit("❌ No video found.")
        print("Search error:", e)
        return

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
        try:
            await status.edit(f"⬆️ Uploading...\nProgress: {percent}")
        except Exception as e:
            print("Upload progress error:", e)

    caption = f"🎬 Title: {title}\n⏱️ Duration: {duration}"
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("▶️ Watch on YouTube", url=url)
    ]])

    try:
        await message.reply_video(
            video=file_name,
            caption=caption,
            thumb=thumb_file if os.path.exists(thumb_file) else None,
            reply_markup=buttons,
            progress=upload_progress
        )
    except Exception as e:
        await message.reply("❌ ভিডিও পাঠাতে সমস্যা হয়েছে।")
        print("Upload error:", e)

    await status.delete()

    # -------------------- ফাইল ডিলিট --------------------
    for f in [file_name, thumb_file]:
        if os.path.exists(f):
            os.remove(f)