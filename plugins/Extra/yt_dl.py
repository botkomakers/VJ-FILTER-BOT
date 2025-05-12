import os
import time
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

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

def progress_hook_func(status_msg, start_time, status_message_obj):
    def hook(d):
        if d['status'] == 'downloading':
            current = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percent = current * 100 / total
            elapsed = time.time() - start_time
            speed = current / elapsed if elapsed > 0 else 0

            bar = f"[{'█' * int(percent // 5)}{'-' * (20 - int(percent // 5))}]"
            text = (
                f"{status_msg}\n\n"
                f"{bar} {percent:.2f}%\n"
                f"{current // (1024 * 1024)}MB / {total // (1024 * 1024)}MB\n"
                f"Speed: {int(speed / 1024)} KB/s"
            )

            try:
                asyncio.run_coroutine_threadsafe(status_message_obj.edit(text), asyncio.get_event_loop())
            except Exception:
                pass
    return hook

@Client.on_message(filters.command("video") & filters.private)
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /video [ভিডিও নাম]")

    status = await message.reply(f"🔍 {query} এর জন্য YouTube-এ অনুসন্ধান করছি...")

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
        "progress_hooks": [progress_hook_func("⬇️ ডাউনলোড হচ্ছে...", start_time, status)],
        "cookiefile": "youtube_cookies.txt",
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

    try:
        upload_status = await message.reply("📤 আপলোড শুরু হচ্ছে...")
        await message.reply_video(
            video=video_filename,
            caption=caption,
            thumb=thumbnail if thumbnail and os.path.exists(thumbnail) else None,
            reply_markup=buttons
        )
        await upload_status.delete()
    except Exception as e:
        await message.reply("❌ ভিডিও পাঠাতে সমস্যা হয়েছে।")
        print("Upload error:", e)

    await status.delete()

    for f in [video_filename, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)