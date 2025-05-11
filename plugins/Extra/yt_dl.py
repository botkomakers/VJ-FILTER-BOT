import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch
from youtube_dl import YoutubeDL as VideoDL
from yt_dlp import YoutubeDL as AudioDL

# -------------------- Shared Helper --------------------

def sanitize_filename(name: str) -> str:
    return ''.join(c if c.isalnum() else '_' for c in name)[:50]

def download_thumbnail(url: str, filename: str) -> str:
    try:
        with open(filename, "wb") as f:
            f.write(requests.get(url).content)
        return filename
    except Exception as e:
        print("Thumbnail download error:", e)
        return None

def search_youtube(query: str):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        return results[0]
    except Exception as e:
        print("YouTube search error:", e)
        return None

# -------------------- VIDEO HANDLER --------------------

@Client.on_message(filters.command("video") & (filters.private | filters.group))
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /video ভিডিও নাম")

    status = await message.reply(f"🔍 `{query}` এর জন্য YouTube-এ খোঁজা হচ্ছে...")

    video = search_youtube(query)
    if not video:
        return await status.edit("❌ ভিডিও খুঁজে পাওয়া যায়নি।")

    url = f"https://www.youtube.com{video['url_suffix']}"
    title, duration, thumb_url = video['title'], video['duration'], video['thumbnails'][0]
    filename_base = sanitize_filename(title)
    video_file = f"{filename_base}.mp4"
    thumb_file = f"{filename_base}.jpg"

    await status.edit("📥 ভিডিও ডাউনলোড হচ্ছে...")

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": video_file,
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with VideoDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ydl.prepare_filename(info)
    except Exception as e:
        print("Video download error:", e)
        return await status.edit("❌ ভিডিও ডাউনলোডে সমস্যা হয়েছে।")

    thumbnail = download_thumbnail(thumb_url, thumb_file)

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("▶️ YouTube", url=url),
        InlineKeyboardButton("🎵 অডিও চাই", callback_data=f"audio|{url}")
    ]])

    await message.reply_video(
        video=video_file,
        caption=f"🎬 **শিরোনাম:** {title}\n⏱️ **সময়কাল:** {duration}",
        thumb=thumbnail if thumbnail and os.path.exists(thumbnail) else None,
        reply_markup=buttons
    )

    await status.delete()

    for file in [video_file, thumb_file]:
        if file and os.path.exists(file):
            os.remove(file)

# -------------------- SONG HANDLER --------------------

# -------------------- SONG HANDLER WITH FORMAT OPTIONS --------------------

from pyrogram.types import CallbackQuery

@Client.on_message(filters.command("song") & filters.private)
async def song_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: /song গান নাম দিন")

    status = await message.reply(f"🔎 `{query}` এর জন্য অনুসন্ধান চলছে...")

    video = search_youtube(query)
    if not video:
        return await status.edit("❌ গান খুঁজে পাওয়া যায়নি।")

    url = f"https://www.youtube.com{video['url_suffix']}"
    title, duration = video['title'], video['duration']
    thumb_url = video['thumbnails'][0]

    # Cache for callback
    await client.set_chat_data(message.chat.id, {
        "title": title, "duration": duration, "url": url, "thumb": thumb_url
    })

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎧 MP3", callback_data="song_format|mp3")],
        [InlineKeyboardButton("🎶 M4A", callback_data="song_format|m4a")],
        [InlineKeyboardButton("🔊 320kbps", callback_data="song_format|320")],
    ])

    await status.edit("আপনি কোন ফরম্যাটে গানটি ডাউনলোড করতে চান?", reply_markup=buttons)


# -------------------- CALLBACK HANDLER FOR SONG FORMATS --------------------

@Client.on_callback_query(filters.regex(r"song_format\|"))
async def song_format_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()

    format_type = callback_query.data.split("|")[1]
    chat_data = await client.get_chat_data(callback_query.message.chat.id)
    if not chat_data:
        return await callback_query.message.edit("❌ আগের তথ্য পাওয়া যায়নি। দয়া করে আবার `/song` কমান্ড দিন।")

    url, title, duration, thumb_url = chat_data["url"], chat_data["title"], chat_data["duration"], chat_data["thumb"]
    safe_title = sanitize_filename(title)
    thumb_file = f"{safe_title}.jpg"

    format_map = {
        "mp3": "bestaudio[ext=mp3]",
        "m4a": "bestaudio[ext=m4a]",
        "320": "bestaudio[abr>320]"
    }

    ydl_opts = {
        "format": format_map.get(format_type, "bestaudio"),
        "outtmpl": f"{safe_title}.{format_type}",
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format_type,
            'preferredquality': '320' if format_type == "320" else '192',
        }] if format_type in ["mp3", "320"] else []
    }

    status = await callback_query.message.edit(f"⏬ `{title}` গানটি `{format_type}` ফরম্যাটে ডাউনলোড হচ্ছে...")

    try:
        with AudioDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_file = ydl.prepare_filename(info)
    except Exception as e:
        print(e)
        return await status.edit("❌ অডিও ডাউনলোডে সমস্যা হয়েছে।")

    thumbnail = download_thumbnail(thumb_url, thumb_file)

    await callback_query.message.reply_audio(
        audio=final_file,
        title=title,
        performer="YouTube",
        caption=f"🎧 **শিরোনাম:** {title}\n⏱️ **সময়কাল:** {duration}",
        thumb=thumbnail if thumbnail and os.path.exists(thumbnail) else None
    )

    await status.delete()
    for f in [final_file, thumb_file]:
        if f and os.path.exists(f):
            os.remove(f)