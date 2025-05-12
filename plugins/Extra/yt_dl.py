import os
import asyncio
import time
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

FORMAT_CACHE = {}

@Client.on_message(filters.command("video") & filters.private)
async def video_handler(client, message: Message):
    query = ' '.join(message.command[1:])
    if not query.startswith("http"):
        return await message.reply("Usage: `/video [YouTube link]`", quote=True)

    msg = await message.reply("🔍 Extracting formats...")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "forcejson": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
    except Exception as e:
        print(e)
        return await msg.edit("❌ Failed to extract video info.")

    title = info.get("title", "Unknown Title")
    thumbnail = info.get("thumbnail")
    formats = info.get("formats", [])

    keyboard = []
    FORMAT_CACHE[message.from_user.id] = {}

    for f in formats:
        f_id = f.get("format_id")
        ext = f.get("ext")
        resolution = f.get("format_note") or f.get("height", "audio")
        filesize = f.get("filesize") or f.get("filesize_approx")
        if not f_id or not ext or not filesize:
            continue

        size_mb = round(filesize / 1024 / 1024, 2)
        label = f"✅ {resolution} - {size_mb}MB ({ext})"

        FORMAT_CACHE[message.from_user.id][f_id] = {
            "url": query,
            "format_id": f_id,
            "ext": ext,
            "title": title
        }

        keyboard.append([InlineKeyboardButton(label, callback_data=f"yt_{f_id}")])

    if not keyboard:
        return await msg.edit("❌ No downloadable formats found.")

    await msg.edit(
        f"📹 **{title}**\n\nFormats for download ⤵️",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex(r"yt_"))
async def quality_button(client, callback_query):
    await callback_query.answer()
    f_id = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    data = FORMAT_CACHE.get(user_id, {}).get(f_id)
    if not data:
        return await callback_query.message.edit("❌ Expired or invalid format.")

    msg = await callback_query.message.edit("⬇️ Downloading...")

    file_name = f"{int(time.time())}.{data['ext']}"

    ydl_opts = {
        "format": data["format_id"],
        "outtmpl": file_name,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([data["url"]])
    except Exception as e:
        print("Download error:", e)
        return await msg.edit("❌ Download failed.")

    try:
        await callback_query.message.reply_video(
            video=file_name,
            caption=f"🎬 {data['title']}",
            quote=True
        )
        await msg.delete()
    except Exception as e:
        await msg.edit("❌ Upload failed.")
        print("Upload error:", e)

    if os.path.exists(file_name):
        os.remove(file_name)