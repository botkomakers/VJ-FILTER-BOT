from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
import requests
import os
import asyncio

# /song কমান্ড হ্যান্ডলার
@Client.on_message(filters.command("song") & (filters.private | filters.group))
async def song_handler(client, message: Message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("**Usage:** `/song গান বা ভিডিও নাম`")

    status = await message.reply("🔍 Searching...")

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        video = results[0]
        title = video['title']
        duration = video['duration']
        video_id = video['url_suffix'].split('v=')[-1]
        url = f"https://www.youtube.com{video['url_suffix']}"
        thumbnail = video['thumbnails'][0]
    except Exception as e:
        return await status.edit("❌ গান খুঁজে পাওয়া যায়নি!")

    # বাটন তৈরি করা হচ্ছে
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 MP3", callback_data=f"mp3|{video_id}"),
            InlineKeyboardButton("🎥 MP4", callback_data=f"mp4|{video_id}")
        ]
    ])

    caption = f"**শিরোনাম:** {title}\n**সময়কাল:** {duration}\n\n**আপনি কোন ফরম্যাটে চান?**"
    await status.edit(caption, reply_markup=buttons)


# Callback হ্যান্ডলার
@Client.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    os.makedirs("downloads", exist_ok=True)

    data = callback_query.data
    format_type, video_id = data.split("|")
    url = f"https://www.youtube.com/watch?v={video_id}"
    msg = await callback_query.message.edit("⏬ Downloading...")

    try:
        ydl_opts = {
            "format": "bestaudio[ext=m4a]" if format_type == "mp3" else "best[ext=mp4]",
            "outtmpl": "downloads/%(title)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title")
            duration = info.get("duration", 0)
            thumbnail = info.get("thumbnail")

        # থাম্বনেইল ডাউনলোড
        thumb_file = f"downloads/thumb_{video_id}.jpg"
        with open(thumb_file, "wb") as f:
            f.write(requests.get(thumbnail).content)

        # ফাইল পাঠানো
        if format_type == "mp3":
            await callback_query.message.reply_audio(
                audio=filename,
                title=title,
                performer="YouTube",
                duration=duration,
                thumb=thumb_file
            )
        else:
            await callback_query.message.reply_video(
                video=filename,
                caption=f"🎬 {title}",
                duration=duration,
                thumb=thumb_file
            )

        await msg.delete()

        # ফাইল পরিষ্কার
        os.remove(filename)
        os.remove(thumb_file)

    except Exception as e:
        await msg.edit("❌ ডাউনলোডে সমস্যা হয়েছে!")
        print(e)