import os
import time
import asyncio
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
            text = f"⬇️ ডাউনলোড হচ্ছে...\nপ্রগতি: {percent}\nগতি: {speed}\nETA: {eta}s"
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
        return await message.reply("ব্যবহার: /video [YouTube লিংক]")

    if "youtube.com/watch?v=" not in query and "youtu.be/" not in query:
        return await message.reply("❌ একটি বৈধ YouTube ভিডিও লিংক প্রদান করুন।")

    status = await message.reply("🔍 ভিডিও তথ্য সংগ্রহ করা হচ্ছে...")

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
        return await status.edit("❌ ভিডিও তথ্য সংগ্রহে ব্যর্থ।")

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

    # MP3 অপশন যোগ করুন
    buttons.append([
        InlineKeyboardButton("✅ MP3 অডিও", callback_data=f"yt|bestaudio|{query}")
    ])

    if not buttons:
        return await status.edit("❌ ডাউনলোডযোগ্য কোনো ফরম্যাট পাওয়া যায়নি।")

    thumb_file = sanitize_filename(title) + ".jpg"
    download_thumbnail(thumbnail, thumb_file)

    await status.edit(
        f"📹 **{title}**\n\nডাউনলোডের জন্য ফরম্যাট নির্বাচন করুন ⤵️",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------- Callback হ্যান্ডলার --------------------
@Client.on_callback_query(filters.regex("^yt\\|"))
async def format_button_handler(client, query: CallbackQuery):
    await query.answer()
    _, format_id, video_url = query.data.split("|")
    status = await query.message.edit("📥 নির্বাচিত ফরম্যাট ডাউনলোড হচ্ছে...")

    file_name = f"yt_{int(time.time())}.mp4"
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
        return await status.edit("❌ ডাউনলোড ব্যর্থ হয়েছে।")

    # থাম্বনেইল
    thumb_file = None
    if info.get('thumbnail'):
        thumb_file = sanitize_filename(info['title']) + ".jpg"
        download_thumbnail(info['thumbnail'], thumb_file)

    # ভিডিও বা অডিও চেক
    is_audio = format_id == "bestaudio"
    media_caption = f"🎬 {info.get('title', 'Untitled')}"

    async def upload_progress(current, total):
        percent = f"{(current / total) * 100:.1f}%"
        try:
            await status.edit(f"⬆️ আপলোড হচ্ছে...\nপ্রগতি: {percent}")
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
        await query.message.reply("❌ পাঠাতে ব্যর্থ হয়েছে।")
        print(e)

    for f in [file_name, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)

# -------------------- বট চালু করুন --------------------
if __name__ == "__main__":
    from pyrogram import Client
    import asyncio

    # আপনার API_ID, API_HASH, এবং BOT_TOKEN এখানে প্রদান করুন
    API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
    API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

    app = Client("yt_dl_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

    app.run()