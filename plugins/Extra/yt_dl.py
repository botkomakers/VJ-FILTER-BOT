import os
import time
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

# -------------------- ইউটিলিটি ফাংশন --------------------

def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]

def download_thumbnail(url: str, filename: str):
    try:
        response = requests.get(url)
        if response.ok:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"Thumbnail download error: {e}")
    return None

async def progress_hook(current, total, message, status_msg, start_time):
    now = time.time()
    diff = now - start_time
    if diff == 0:
        diff = 1
    percentage = current * 100 / total
    speed = current / diff
    eta = (total - current) / speed
    progress_bar = f"[{'█' * int(percentage / 5)}{'-' * (20 - int(percentage / 5))}]"
    progress_text = f"{status_msg}\n\n{progress_bar} {percentage:.2f}%\n" \
                    f"Transferred: {current / (1024 ** 2):.2f}MB of {total / (1024 ** 2):.2f}MB\n" \
                    f"Speed: {speed / (1024):.2f} KB/s\nETA: {int(eta)}s"
    try:
        await message.edit(progress_text)
    except:
        pass

# -------------------- ভিডিও হ্যান্ডলার --------------------

@Client.on_message(filters.command("video") & filters.private)
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /video [ভিডিও নাম]")

    status = await message.reply(f"🔍 `{query}` এর জন্য YouTube-এ অনুসন্ধান করছি...")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        video = results[0]
        url = f"https://www.youtube.com{video['url_suffix']}"
        title = video['title']
        duration = video['duration']
        thumbnail_url = video['thumbnails'][0]
    except Exception as e:
        await status.edit("❌ ভিডিও খুঁজে পাওয়া যায়নি।")
        print("Search error:", e)
        return

    await status.edit("📥 ভিডিও ডাউনলোড শুরু হচ্ছে...")
    safe_title = sanitize_filename(title)
    video_filename = f"{safe_title}.mp4"
    thumb_file = f"{safe_title}.jpg"
    start_time = time.time()

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": video_filename,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [
            lambda d: asyncio.create_task(progress_hook(
                d.get('downloaded_bytes', 0),
                d.get('total_bytes', 1),
                status,
                "⬇️ ডাউনলোড হচ্ছে...",
                start_time
            )) if d.get('status') == 'downloading' else None
        ]
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        await status.edit("❌ ভিডিও ডাউনলোডে সমস্যা হয়েছে।")
        print("yt_dlp error:", e)
        return

    thumbnail = download_thumbnail(thumbnail_url, thumb_file)
    caption = f"🎬 শিরোনাম: {title}\n⏱️ সময়কাল: {duration}"
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("▶️ YouTube এ দেখুন", url=url)
    ]])

    async def upload_progress(current, total):
        await progress_hook(current, total, status, "⏫ আপলোড হচ্ছে...", start_time)

    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=video_filename,
            caption=caption,
            thumb=thumbnail if thumbnail and os.path.exists(thumbnail) else None,
            reply_markup=buttons,
            progress=upload_progress
        )
    except Exception as e:
        await message.reply("❌ ভিডিও পাঠাতে সমস্যা হয়েছে।")
        print("Upload error:", e)

    await status.delete()
    for f in [video_filename, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)