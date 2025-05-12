import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL

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
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '0 KiB/s')
            eta = d.get('eta', 0)
            text = f"⬇️ Downloading...\nProgress: {percent}\nSpeed: {speed}\nETA: {eta}s"
            try:
                await msg.edit(text)
                last_time[0] = now
            except: pass

# -------------------- /video হ্যান্ডলার --------------------
@Client.on_message(filters.command("video") & filters.private)
async def video_command_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /video [YouTube link]")

    if "youtube.com/watch?v=" not in query and "youtu.be/" not in query:
        return await message.reply("❌ Please provide a valid YouTube video link.")

    status = await message.reply("🔍 Extracting video info...")

    ydl_opts = {
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
    except Exception as e:
        print(f"Extraction error: {e}")
        return await status.edit("❌ Failed to extract video info.")

    title = info.get('title', 'No Title')
    thumbnail = info.get('thumbnail')
    formats = info.get('formats', [])

    buttons = []
    unique = set()
    for f in formats:
        fmt = f.get("format_note")
        ext = f.get("ext")
        if fmt and ext and f.get("filesize") and f.get("vcodec") != "none" and f.get("acodec") != "none":
            tag = f"{fmt}-{ext}"
            if tag not in unique:
                unique.add(tag)
                size = round(f["filesize"] / 1024 / 1024, 2)
                buttons.append([
                    InlineKeyboardButton(
                        f"✅ {fmt.upper()} - {size}MB",
                        callback_data=f"yt|{f['format_id']}|{query}"
                    )
                ])

    # -------------------- MP3 অপশন --------------------
    buttons.append([
        InlineKeyboardButton("✅ MP3 Audio", callback_data=f"yt|bestaudio|{query}")
    ])

    if not buttons:
        return await status.edit("❌ No downloadable formats found.")

    thumb_file = sanitize_filename(title) + ".jpg"
    download_thumbnail(thumbnail, thumb_file)

    await status.delete()

    await message.reply_photo(
        photo=thumb_file if os.path.exists(thumb_file) else None,
        caption=f"📹 {title}\n\nFormats for download ⤵️",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    if os.path.exists(thumb_file):
        os.remove(thumb_file)

# -------------------- Callback হ্যান্ডলার --------------------
@Client.on_callback_query(filters.regex(r"^yt\|"))
async def format_button_handler(client, query: CallbackQuery):
    await query.answer()
    _, format_id, video_url = query.data.split("|")
    status = await query.message.edit("📥 Downloading selected format...")

    is_audio = format_id == "bestaudio"
    ext = "mp3" if is_audio else "mp4"
    file_name = f"yt_{int(time.time())}.{ext}"
    last_time = [time.time()]

    ydl_opts = {
        "format": "bestaudio" if is_audio else f"{format_id}+bestaudio/best",
        "outtmpl": file_name,
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4" if not is_audio else None,
        "progress_hooks": [lambda d: client.loop.create_task(progress_hook(d, status, last_time))],
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }] if is_audio else []
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url)
    except Exception as e:
        print(f"Download error: {e}")
        return await status.edit("❌ Download failed.")

    # -------------------- থাম্বনেইল --------------------
    thumb_file = None
    if info.get('thumbnail'):
        thumb_file = sanitize_filename(info['title']) + ".jpg"
        download_thumbnail(info['thumbnail'], thumb_file)

    # -------------------- ভিডিও হোক বা অডিও --------------------
    media_caption = f"🎬 {info.get('title', 'Untitled')}"

    async def upload_progress(current, total):
        percent = f"{(current / total) * 100:.1f}%"
        try:
            await status.edit(f"⬆️ Uploading...\nProgress: {percent}")
        except:
            pass

    try:
        if is_audio:
            await query.message.reply_audio(
                audio=file_name,
                caption=media_caption,
                thumb=thumb_file if os.path.exists(thumb_file) else None,
                progress=upload_progress
            )
        else:
            await query.message.reply_video(
                video=file_name,
                caption=media_caption,
                thumb=thumb_file if os.path.exists(thumb_file) else None,
                progress=upload_progress
            )
        await status.delete()
    except Exception as e:
        await query.message.reply("❌ Sending failed.")
        print(e)

    for f in [file_name, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)