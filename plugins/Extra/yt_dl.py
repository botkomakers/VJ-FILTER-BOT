import os
import time
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
from config import temp  # প্রয়োজন হলে

# ----------- ফাইলনেম সেনিটাইজ ----------
def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]

# ----------- থাম্বনেইল ডাউনলোড ----------
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

# ----------- ভিডিও কমান্ড হ্যান্ডলার ----------
@Client.on_message(filters.command("video") & filters.private)
async def video_command_handler(client, message: Message):
    query = ' '.join(message.command[1:]).strip()
    if not query or ("youtube.com" not in query and "youtu.be" not in query):
        return await message.reply("Usage: /video [YouTube link]")

    status = await message.reply("🔍 Fetching video info...")
    await process_youtube_video(client, message, query, status)


# ----------- ইউটিউব ভিডিও প্রসেস ----------
async def process_youtube_video(client, message, url, status_msg):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': 'youtube_cookies.txt',
        'skip_download': True,
        'format': 'best',
        'forcejson': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        await status_msg.edit("❌ Failed to fetch video info.")
        print(e)
        return

    title = info.get("title", "No title")
    duration = info.get("duration_string", "")
    thumb = info.get("thumbnail", "")
    formats = info.get("formats", [])

    # ফরম্যাট বাছাই
    buttons = []
    seen = set()

    for fmt in formats:
        fmt_id = fmt.get("format_id")
        ext = fmt.get("ext")
        height = fmt.get("height")
        filesize = fmt.get("filesize", 0) or fmt.get("filesize_approx", 0)

        if not fmt_id or not filesize or ext not in ["mp4", "webm", "m4a"]:
            continue

        tag = f"{height or ext}"
        if tag in seen:
            continue
        seen.add(tag)

        size_mb = round(filesize / 1024 / 1024, 2)
        label = f"{height}p - {size_mb}MB" if height else f"{ext.upper()} - {size_mb}MB"
        cb_data = f"yt_{fmt_id}|{url}"
        buttons.append([InlineKeyboardButton(f"✅ {label}", callback_data=cb_data)])

    # MP3 বাটন যোগ
    buttons.append([InlineKeyboardButton("✅ MP3 - Audio", callback_data=f"yt_mp3|{url}")])

    caption = f"📹 {title}\n⏱️ Duration: {duration}\n\nFormats for download ⤵️"
    markup = InlineKeyboardMarkup(buttons)

    thumb_file = sanitize_filename(title) + ".jpg"
    download_thumbnail(thumb, thumb_file)

    await status_msg.delete()
    await message.reply_photo(photo=thumb_file if os.path.exists(thumb_file) else None,
                              caption=caption,
                              reply_markup=markup)

    if os.path.exists(thumb_file):
        os.remove(thumb_file)


# ----------- কলে ব্যাক হ্যান্ডলার ----------
@Client.on_callback_query(filters.regex(r"yt_(.+)\|(.+)"))
async def format_button_handler(client, query: CallbackQuery):
    fmt_id, url = query.data.split("|")
    user = query.from_user
    msg = await query.message.edit_text("⬇️ Downloading selected format...")

    # ফাইলনেম তৈরি
    ydl_opts = {
        'format': fmt_id if fmt_id != "mp3" else "bestaudio[ext=m4a]",
        'outtmpl': f"{user.id}_%(title).50s.{'mp3' if fmt_id == 'mp3' else 'mp4'}",
        'cookiefile': 'youtube_cookies.txt',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            file_path = ydl.prepare_filename(info)
            title = info.get("title", "")
            duration = info.get("duration_string", "")
    except Exception as e:
        await msg.edit("❌ Download failed.")
        print(e)
        return

    # আপলোড
    try:
        if fmt_id == "mp3":
            await query.message.reply_audio(
                audio=file_path,
                caption=f"🎵 {title}",
                title=title
            )
        else:
            await query.message.reply_video(
                video=file_path,
                caption=f"🎬 {title}"
            )
    except Exception as e:
        await query.message.reply("❌ Upload failed.")
        print(e)

    await msg.delete()

    # ডিলিট
    if os.path.exists(file_path):
        os.remove(file_path)