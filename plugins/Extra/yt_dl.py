from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL
import os, wget, asyncio

def get_text(message: Message) -> [None, str]:
    if not message.text or " " not in message.text:
        return None
    return message.text.split(None, 1)[1]

@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    query = get_text(message)
    status_msg = await message.reply(f"**🔎 Searching video for:** `{query}`")

    if not query:
        return await status_msg.edit("❌ Example: `/video Arijit Singh new song`")

    try:
        search = SearchVideos(query, offset=1, mode="dict", max_results=1)
        results = search.result()["search_result"][0]
        video_url = results["link"]
        title = results["title"]
        video_id = results["id"]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    except Exception as e:
        return await status_msg.edit(f"❌ Error while searching:\n`{str(e)}`")

    await asyncio.sleep(0.5)
    thumb_file = wget.download(thumbnail_url)

    opts = {
        "format": "bestvideo+bestaudio/best",
        "cookies": os.path.join(os.getcwd(), "youtube_cookies.txt"),
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
        "outtmpl": "%(id)s.%(ext)s",
        "logtostderr": False,
        "quiet": True,
    }

    try:
        with YoutubeDL(opts) as ytdl:
            info = ytdl.extract_info(video_url, download=True)
            video_file = f"{info['id']}.mp4"
    except Exception as e:
        await status_msg.edit(f"❌ ডাউনলোড ব্যর্থ!\n`{str(e)}`")
        if os.path.exists(thumb_file):
            os.remove(thumb_file)
        return

    caption = f"""**🎬 Title:** [{title}]({video_url})
**👤 Requested by:** {message.from_user.mention}"""

    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=open(video_file, "rb"),
            thumb=thumb_file,
            caption=caption,
            file_name=f"{info.get('title', 'video')}.mp4",
            duration=int(info.get("duration", 0)),
            supports_streaming=True,
            reply_to_message_id=message.id
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit(f"✅ ভিডিও ডাউনলোড হয়েছে কিন্তু পাঠাতে সমস্যা:\n`{str(e)}`")

    for f in [video_file, thumb_file]:
        if os.path.exists(f):
            os.remove(f)