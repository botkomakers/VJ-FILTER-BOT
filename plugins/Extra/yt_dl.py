import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

# -------------------- ইন-মেমোরি ইউজার ডেটা --------------------
USER_SONG_DATA = {}

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

    USER_SONG_DATA[message.from_user.id] = {
        "title": title,
        "duration": duration,
        "url": url,
        "thumb": thumb_url
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
    user_id = callback_query.from_user.id
    format_type = callback_query.data.split("|")[1]
    song_data = USER_SONG_DATA.get(user_id)

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
        "mp3": "bestaudio[ext=webm]/bestaudio",
        "m4a": "bestaudio[ext=m4a]/bestaudio",
        "320": "bestaudio[abr>320]/bestaudio"
    }

    ydl_opts = {
        "format": format_map.get(format_type, "bestaudio"),
        "outtmpl": audio_file,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3' if format_type in ['mp3', '320'] else 'm4a',
            'preferredquality': '320' if format_type == "320" else '192',
        }]
    }

    status = await callback_query.message.edit(f"⏬ `{title}` গানটি `{format_type}` ফরম্যাটে ডাউনলোড হচ্ছে...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_file = ydl.prepare_filename(info)
            if not final_file.endswith(f".{format_type}"):
                final_file = audio_file
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

    USER_SONG_DATA.pop(user_id, None)

# -------------------- /video হ্যান্ডলার --------------------
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

    await status.edit("📥 ভিডিও ডাউনলোড হচ্ছে...")  

    safe_title = sanitize_filename(title)
    video_filename = f"{safe_title}.mp4"
    thumb_file = f"{safe_title}.jpg"

    ydl_opts = {  
        "format": "best[ext=mp4]",  
        "outtmpl": video_filename,  
        "cookiefile": "youtube_cookies.txt",  
        "quiet": True,  
        "no_warnings": True,  
    }

    try:  
        with YoutubeDL(ydl_opts) as ydl:  
            ydl.download([url])  
    except Exception as e:  
        await status.edit("❌ ডাউনলোডে সমস্যা হয়েছে।")  
        print("yt_dlp error:", e)  
        return  

    thumbnail = download_thumbnail(thumbnail_url, thumb_file)

    caption = f"🎬 শিরোনাম: {title}\n⏱️ সময়কাল: {duration}"  
    buttons = InlineKeyboardMarkup([[  
        InlineKeyboardButton("▶️ YouTube এ দেখুন", url=url)  
    ]])  

    try:  
        await message.reply_video(  
            video=video_filename,  
            caption=caption,  
            thumb=thumbnail if thumbnail and os.path.exists(thumbnail) else None,  
            reply_markup=buttons  
        )  
    except Exception as e:  
        await message.reply("❌ ভিডিও পাঠাতে সমস্যা হয়েছে।")  
        print("Upload error:", e)  

    await status.delete()  

    for f in [video_filename, thumb_file]:  
        if f and os.path.exists(f):
            os.remove(f)








import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

# ইউটিউব লিংক চেক করার জন্য regex
YOUTUBE_URL_REGEX = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

def is_youtube_url(text: str) -> bool:
    return re.match(YOUTUBE_URL_REGEX, text) is not None

def sanitize_filename(title: str):
    return ''.join(c if c.isalnum() else '_' for c in title)[:50]

@Client.on_message(filters.command("videos") & filters.private)
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Usage: `/video [নাম বা ইউটিউব লিংক]`", quote=True)

    status = await message.reply("🔍 অনুসন্ধান চলছে...")

    if is_youtube_url(query):
        url = query
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title")
                duration = info.get("duration_string", "N/A")
                thumbnail_url = info.get("thumbnail")
        except Exception as e:
            await status.edit("❌ ইউটিউব লিংক থেকে তথ্য নিতে সমস্যা হয়েছে।")
            print("Link extract error:", e)
            return
    else:
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            if not results:
                return await status.edit("❌ ভিডিও খুঁজে পাওয়া যায়নি।")
            video = results[0]
            url = f"https://www.youtube.com{video['url_suffix']}"
            title = video['title']
            duration = video['duration']
            thumbnail_url = video['thumbnails'][0]
        except Exception as e:
            await status.edit("❌ অনুসন্ধানে সমস্যা হয়েছে।")
            print("Search error:", e)
            return

    await status.edit("📥 ভিডিও ডাউনলোড হচ্ছে...")

    safe_title = sanitize_filename(title)
    video_filename = f"{safe_title}.mp4"
    thumb_file = f"{safe_title}.jpg"

    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": video_filename,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        await status.edit("❌ ডাউনলোডে সমস্যা হয়েছে।")
        print("yt_dlp error:", e)
        return

    try:
        with open(thumb_file, "wb") as f:
            f.write(requests.get(thumbnail_url).content)
    except:
        thumb_file = None

    caption = f"🎬 **শিরোনাম:** {title}\n⏱️ **সময়কাল:** {duration}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("▶️ ইউটিউবে দেখুন", url=url)]])

    try:
        await message.reply_video(
            video=video_filename,
            caption=caption,
            thumb=thumb_file if thumb_file and os.path.exists(thumb_file) else None,
            reply_markup=buttons
        )
    except Exception as e:
        await message.reply("❌ ভিডিও পাঠাতে সমস্যা হয়েছে।")
        print("Upload error:", e)

    await status.delete()

    for f in [video_filename, thumb_file]:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass