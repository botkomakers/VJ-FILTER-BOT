import os
import time
import requests
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery

# ফাইলনেম সেনিটাইজ
def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]

# থাম্বনেইল ডাউনলোড
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

# প্রগ্রেস হুক
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

# ফরম্যাট বাটন হ্যান্ডলার
@Client.on_callback_query(filters.regex("^yt\\|"))
async def format_button_handler(client, query: CallbackQuery):
    await query.answer()
    _, format_id, video_url = query.data.split("|")
    status = await query.message.edit("📥 Downloading selected format...")

    # ভিডিও ফরম্যাটের এক্সটেনশন নির্ধারণের জন্য fallback
    file_extension = "mp4"  # ডিফল্ট ফরম্যাট

    # ফরম্যাট আইডি থেকে এক্সটেনশন বের করা
    try:
        file_extension = format_id.split("-")[1]  # ডিলিমিটেড ফরম্যাট আইডি থেকে এক্সটেনশন বের করা
    except IndexError:
        pass  # যদি কোনো সমস্যা হয় তবে ডিফল্ট mp4 থাকবে

    file_name = f"yt_{int(time.time())}.{file_extension}"  # ফাইল নামের এক্সটেনশন যোগ করা
    last_time = [time.time()]

    ydl_opts = {
        "format": format_id,
        "outtmpl": file_name,
        "cookiefile": "youtube_cookies.txt",
        "progress_hooks": [lambda d: client.loop.create_task(progress_hook(d, status, last_time))],
        "quiet": True,
        "no_warnings": True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url)
    except Exception as e:
        print(f"Download error: {e}")
        return await status.edit("❌ Download failed.")

    # থাম্বনেইল
    thumb_file = None
    if info.get('thumbnail'):
        thumb_file = sanitize_filename(info['title']) + ".jpg"
        download_thumbnail(info['thumbnail'], thumb_file)

    # ভিডিও হোক বা অডিও
    is_audio = format_id == "bestaudio"
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

    # ফাইল ডিলিট
    for f in [file_name, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)