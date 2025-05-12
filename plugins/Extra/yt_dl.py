import os
import time
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
import subprocess  # FFmpeg ব্যবহার করার জন্য

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
            except:
                pass

# -------------------- /video হ্যান্ডলার --------------------
@Client.on_message(filters.command("video") & filters.private)
async def video_command_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("❌ Usage: /video [YouTube link]", parse_mode="markdown")

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
        if fmt and ext and f.get("filesize") and f.get("vcodec") != "none":
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

    # MP3 Option
    buttons.append([
        InlineKeyboardButton("✅ MP3 Audio", callback_data=f"yt|bestaudio|{query}")
    ])

    if not buttons:
        return await status.edit("❌ No downloadable formats found.")

    # Add Thumbnail
    thumb_file = sanitize_filename(title) + ".jpg"
    download_thumbnail(thumbnail, thumb_file)

    # Send the thumbnail and format options in a single message
    await status.edit(
        f"📹 {title}\n\nFormats for download ⤵️",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    # Send the thumbnail image along with the format options in one message
    await message.reply_photo(
        photo=thumb_file if os.path.exists(thumb_file) else None,
        caption=f"📹 {title}\n\nChoose a format below to download:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    if os.path.exists(thumb_file):
        os.remove(thumb_file)

# -------------------- Callback হ্যান্ডলার --------------------
@Client.on_callback_query(filters.regex("^yt|"))
async def format_button_handler(client, query: CallbackQuery):
    await query.answer()
    _, format_id, video_url = query.data.split("|")
    status = await query.message.edit("📥 Downloading selected format...")

    video_file_name = f"yt_video_{int(time.time())}.mp4"
    audio_file_name = f"yt_audio_{int(time.time())}.mp3"
    last_time = [time.time()]

    # Set options for downloading video and audio
    ydl_opts = {
        "format": format_id,
        "outtmpl": video_file_name,
        "cookiefile": "youtube_cookies.txt",
        "progress_hooks": [lambda d: client.loop.create_task(progress_hook(d, status, last_time))],
        "quiet": True,
        "no_warnings": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url)
    except Exception as e:
        print(f"Download error: {e}")
        return await status.edit("❌ Download failed.")

    # Download audio
    audio_ydl_opts = {
        "format": "bestaudio",
        "outtmpl": audio_file_name,
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True
    }

    try:
        with YoutubeDL(audio_ydl_opts) as ydl:
            audio_info = ydl.extract_info(video_url)
    except Exception as e:
        print(f"Download error: {e}")
        return await status.edit("❌ Audio download failed.")

    # Merge video and audio using FFmpeg
    merged_file_name = f"yt_merged_{int(time.time())}.mp4"
    try:
        # Command to merge video and audio using FFmpeg
        command = [
            "ffmpeg",
            "-i", video_file_name,
            "-i", audio_file_name,
            "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
            "-map", "0:v:0", "-map", "1:a:0",
            merged_file_name
        ]
        subprocess.run(command, check=True)

    except Exception as e:
        print(f"Merging error: {e}")
        return await status.edit("❌ Failed to merge video and audio.")

    # Upload merged file
    thumb_file = None
    if video_info.get('thumbnail'):
        thumb_file = sanitize_filename(video_info['title']) + ".jpg"
        download_thumbnail(video_info['thumbnail'], thumb_file)

    media_caption = f"🎬 {video_info.get('title', 'Untitled')}"

    async def upload_progress(current, total):
        percent = f"{(current / total) * 100:.1f}%"
        try:
            await status.edit(f"⬆️ Uploading...\nProgress: {percent}")
        except:
            pass

    try:
        await query.message.reply_video(
            video=merged_file_name,
            caption=media_caption,
            thumb=thumb_file if os.path.exists(thumb_file) else None,
            progress=upload_progress
        )
        await status.delete()
    except Exception as e:
        await query.message.reply("❌ Sending failed.")
        print(e)

    for f in [video_file_name, audio_file_name, merged_file_name, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)