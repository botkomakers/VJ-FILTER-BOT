import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL as AudioDL
from youtube_search import YoutubeSearch


# -------------------- ইউটিউব সার্চ হেল্পার --------------------

def search_youtube(query: str):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        return results[0] if results else None
    except Exception as e:
        print(f"Search error: {e}")
        return None


# -------------------- ফাইলনেম সেনিটাইজ --------------------

def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]


# -------------------- থাম্বনেইল ডাউনলোডার --------------------

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


# -------------------- /song হ্যান্ডলার --------------------

@Client.on_message(filters.command("song") & filters.private)
async def song_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: `/song গান নাম দিন`", quote=True)

    status = await message.reply(f"🔎 `{query}` এর জন্য অনুসন্ধান চলছে...", quote=True)

    video = search_youtube(query)
    if not video:
        return await status.edit("❌ গান খুঁজে পাওয়া যায়নি।")

    url = f"https://www.youtube.com{video['url_suffix']}"
    title, duration = video['title'], video['duration']
    thumb_url = video['thumbnails'][0]

    # cache manually
    message.chat.song_data = {
        "title": title, "duration": duration, "url": url, "thumb": thumb_url
    }

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎧 MP3", callback_data="song_format|mp3")],
        [InlineKeyboardButton("🎶 M4A", callback_data="song_format|m4a")],
        [InlineKeyboardButton("🔊 320kbps", callback_data="song_format|320")]
    ])

    await status.edit("আপনি কোন ফরম্যাটে গানটি ডাউনলোড করতে চান?", reply_markup=buttons)


# -------------------- ফরম্যাট বাটনের জন্য Callback --------------------

@Client.on_callback_query(filters.regex(r"song_format\|"))
async def song_format_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()

    format_type = callback_query.data.split("|")[1]
    song_data = getattr(callback_query.message.chat, "song_data", None)

    if not song_data:
        return await callback_query.message.edit("❌ আগের তথ্য পাওয়া যায়নি। দয়া করে আবার `/song` দিন।")

    url = song_data["url"]
    title = song_data["title"]
    duration = song_data["duration"]
    thumb_url = song_data["thumb"]

    safe_title = sanitize_filename(title)
    audio_file = f"{safe_title}.{format_type}"
    thumb_file = f"{safe_title}.jpg"

    format_map = {
        "mp3": "bestaudio[ext=mp3]",
        "m4a": "bestaudio[ext=m4a]",
        "320": "bestaudio[abr>320]"
    }

    ydl_opts = {
        "format": format_map.get(format_type, "bestaudio"),
        "outtmpl": audio_file,
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
        return await status.edit("❌ ডাউনলোডে সমস্যা হয়েছে।")

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