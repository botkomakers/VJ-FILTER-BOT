import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_search import YoutubeSearch

# Use YoutubeDL or yt_dlp based on function
from youtube_dl import YoutubeDL as VideoDL
from yt_dlp import YoutubeDL as AudioDL


# ---------------------- VIDEO HANDLER ----------------------

@Client.on_message(filters.command("video") & (filters.private | filters.group))
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("**Usage:** `/video ভিডিও নাম`")

    status_msg = await message.reply(f"🔍 `{query}` এর জন্য YouTube-এ অনুসন্ধান করছি...")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        video = results[0]
        url = f"https://www.youtube.com{video['url_suffix']}"
        title = video['title']
        duration = video['duration']
        thumbnail_url = video['thumbnails'][0]
    except Exception as e:
        await status_msg.edit("❌ ভিডিও খুঁজে পাওয়া যায়নি।")
        print("Search error:", e)
        return

    await status_msg.edit("📥 ভিডিও ডাউনলোড হচ্ছে...")

    safe_title = ''.join(c if c.isalnum() else '_' for c in title)[:50]
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
        with VideoDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        await status_msg.edit("❌ ভিডিও ডাউনলোডে সমস্যা হয়েছে।")
        print("Download error:", e)
        return

    try:
        with open(thumb_file, "wb") as f:
            f.write(requests.get(thumbnail_url).content)
    except Exception as e:
        thumb_file = None
        print("Thumbnail error:", e)

    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("▶️ YouTube এ দেখুন", url=url),
        InlineKeyboardButton("🎵 অডিও চাই", callback_data=f"audio|{url}")
    ]])

    await message.reply_video(
        video=filename,
        caption=f"**🎬 শিরোনাম:** {title}\n⏱️ **সময়কাল:** {duration}",
        thumb=thumb_file if os.path.exists(thumb_file) else None,
        reply_markup=buttons
    )

    await status_msg.delete()

    for f in [video_filename, thumb_file]:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass


# ---------------------- SONG HANDLER ----------------------

@Client.on_message(filters.command("song") & filters.private)
async def song_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("**Usage:** `/song গান নাম`")

    status_msg = await message.reply(f"🔎 Searching for **{query}**...")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        video = results[0]
        url = f"https://www.youtube.com{video['url_suffix']}"
        title = video['title']
        duration = video['duration']
        thumbnail_url = video['thumbnails'][0]
    except Exception:
        await status_msg.edit("❌ গান খুঁজে পাওয়া যায়নি।")
        return

    await status_msg.edit("⏬ Downloading audio...")

    safe_title = ''.join(c if c.isalnum() else '_' for c in title)[:50]
    audio_filename = f"{safe_title}.m4a"
    thumb_file = f"{safe_title}.jpg"

    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "outtmpl": audio_filename,
        "cookiefile": "youtube_cookies.txt",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with AudioDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as e:
        await status_msg.edit("❌ ডাউনলোডে সমস্যা হয়েছে।")
        print(e)
        return

    # Download thumbnail
    try:
        with open(thumb_file, "wb") as f:
            f.write(requests.get(thumbnail_url).content)
    except:
        thumb_file = None

    # Duration in seconds
    duration_sec = 0
    try:
        parts = duration.split(":")
        for i in range(len(parts)):
            duration_sec += int(parts[-(i+1)]) * (60 ** i)
    except:
        duration_sec = None

    await message.reply_audio(
        audio=filename,
        title=title,
        performer="YouTube",
        caption=f"🎵 {title}",
        duration=duration_sec,
        thumb=thumb_file if os.path.exists(thumb_file) else None
    )

    await status_msg.delete()

    # Cleanup
    for f in [filename, thumb_file]:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass