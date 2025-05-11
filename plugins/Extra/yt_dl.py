from pyrogram import Client, filters
from pyrogram.types import Message
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import os, wget, asyncio

def get_text(message: Message) -> [None, str]:
    if not message.text or " " not in message.text:
        return None
    return message.text.split(None, 1)[1]

@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    query = get_text(message)
    status_msg = await message.reply(f"**𝙵𝙸𝙽𝙳𝙸𝙽𝙶 𝚈𝙾𝚄𝚁 𝚅𝙸𝙳𝙴𝙾** `{query}`")

    if not query:
        return await status_msg.edit("❌ Example: `/video Arijit Singh new song`")

    try:
        search = VideosSearch(query, limit=1)
        result = search.result()["result"][0]
        video_url = result["link"]
        title = result["title"]
        video_id = result["id"]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    except Exception as e:
        return await status_msg.edit(f"❌ Error while searching:\n`{str(e)}`")

    await asyncio.sleep(0.5)
    thumb_file = wget.download(thumbnail_url)

    # yt-dlp options with cookies
    opts = {
        "format": "best",
        "cookies": "youtube_cookies.txt",  # Path to your cookie file
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
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(video_url, download=True)
            video_file = f"{ytdl_data['id']}.mp4"
    except Exception as e:
        await status_msg.edit_text(f"**❌ Download Failed!**\n`{str(e)}`")
        if os.path.exists(thumb_file):
            os.remove(thumb_file)
        return

    caption = f"""**🎬 Title:** [{title}]({video_url})
**👤 Requested by:** {message.from_user.mention}"""

    await client.send_video(
        chat_id=message.chat.id,
        video=open(video_file, "rb"),
        thumb=thumb_file,
        caption=caption,
        file_name=f"{ytdl_data.get('title', 'video')}.mp4",
        duration=int(ytdl_data.get("duration", 0)),
        supports_streaming=True,
        reply_to_message_id=message.id
    )
    await status_msg.delete()

    for f in [video_file, thumb_file]:
        if os.path.exists(f):
            os.remove(f)