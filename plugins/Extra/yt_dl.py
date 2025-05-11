from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import os, wget, asyncio

# ইউজারের কমান্ড থেকে সার্চ টেক্সট বের করা
def get_text(message: Message) -> [None, str]:
    if not message.text or " " not in message.text:
        return None
    return message.text.split(None, 1)[1]

@Client.on_message(filters.command(["video", "mp4"]))
async def video_download(client, message: Message):
    query = get_text(message)
    status = await message.reply(f"🔍 **খোঁজা হচ্ছে:** `{query}`")

    if not query:
        return await status.edit("❌ উদাহরণ: `/video Arijit Singh new song`")

    try:
        results = VideosSearch(query, limit=1).result()
        result = results["result"][0]
        video_url = result["link"]
        title = result["title"]
        video_id = result["id"]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    except Exception as e:
        return await status.edit(f"❌ সার্চে সমস্যা:\n`{str(e)}`")

    # থাম্বনেইল নামানো
    thumb_file = wget.download(thumbnail_url)

    # yt-dlp অপশন
    ytdl_opts = {
        "format": "best",
        "cookies": "youtube_cookies.txt",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
        ],
        "outtmpl": "%(id)s.%(ext)s",
        "logtostderr": False,
        "quiet": True,
    }

    try:
        await status.edit("📥 **ভিডিও ডাউনলোড হচ্ছে...**")
        with YoutubeDL(ytdl_opts) as ytdl:
            data = ytdl.extract_info(video_url, download=True)
            video_file = f"{data['id']}.mp4"
    except Exception as e:
        await status.edit(f"❌ ডাউনলোড ব্যর্থ!\n`{str(e)}`")
        if os.path.exists(thumb_file):
            os.remove(thumb_file)
        return

    caption = f"""**🎬 শিরোনাম:** [{title}]({video_url})
**👤 অনুরোধ করেছেন:** {message.from_user.mention}"""

    await client.send_video(
        chat_id=message.chat.id,
        video=open(video_file, "rb"),
        thumb=thumb_file,
        caption=caption,
        file_name=f"{data.get('title', 'video')}.mp4",
        duration=int(data.get("duration", 0)),
        supports_streaming=True,
        reply_to_message_id=message.id
    )
    await status.delete()

    # ক্লিন আপ
    for f in [video_file, thumb_file]:
        if os.path.exists(f):
            os.remove(f)