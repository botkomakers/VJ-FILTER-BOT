
from __future__ import unicode_literals

import os, requests, asyncio, math, time, wget
from pyrogram import filters, Client
from pyrogram.types import Message
from info import CHNL_LNK
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL


@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    user_id = message.from_user.id 
    user_name = message.from_user.first_name 
    rpk = "["+user_name+"](tg://user?id="+str(user_id)+")"
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = await message.reply(f"**ѕєαrchíng чσur ѕσng...!\n {query}**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]       
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        performer = f"[NETWORKS™]" 
        duration = results[0]["duration"]
        url_suffix = results[0]["url_suffix"]
        views = results[0]["views"]
    except Exception as e:
        print(str(e))
        return await m.edit("Example: /song vaa vaathi song")

    await m.edit("**dσwnlσαdíng чσur ѕσng...!**")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        cap = f"**BY›› [UPDATE]({CHNL_LNK})**"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        await message.reply_audio(
            audio_file,
            caption=cap,            
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )            
        await m.delete()
    except Exception as e:
        await m.edit("**🚫 𝙴𝚁𝚁𝙾𝚁 🚫**")
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

def get_text(message: Message) -> [None,str]:
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None


@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)
    if not urlissed:
        return await message.reply("Example: /video Arijit Singh")

    pablo = await message.reply(f"**𝙵𝙸𝙽𝙳𝙸𝙽𝙶 𝚈𝙾𝚄𝚁 𝚅𝙸𝙳𝙴𝙾...**")

    # Check if the input is a YouTube URL
    if "youtube.com/watch?v=" in urlissed or "youtu.be/" in urlissed:
        url = urlissed
        # Get video ID for thumbnail
        from urllib.parse import parse_qs, urlparse
        query = urlparse(url).query
        video_id = parse_qs(query).get("v", [None])[0]
        if not video_id and "youtu.be/" in url:
            video_id = url.split("/")[-1]
        thum = "Video"
        mo = url
    else:
        # Search by keywords
        search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
        mi = search.result()
        mio = mi["search_result"]
        url = mio[0]["link"]
        thum = mio[0]["title"]
        video_id = mio[0]["id"]
        mo = mio[0]["link"]

    kekme = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    try:
        sedlyf = f"thumb_{video_id}.jpg"
        thumb_data = requests.get(kekme, allow_redirects=True)
        with open(sedlyf, 'wb') as f:
            f.write(thumb_data.content)
    except Exception as e:
        sedlyf = None
        print("Thumbnail download error:", e)

    # yt-dlp download
    opts = {
        "format": "best",
        "addmetadata": True,
        "prefer_ffmpeg": True,
        "outtmpl": "%(id)s.%(ext)s",
        "quiet": True,
        "geo_bypass": True,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }]
    }

    try:
        with YoutubeDL(opts) as ytdl:
            info = ytdl.extract_info(url, download=True)
            filename = f"{info['id']}.mp4"
    except Exception as e:
        return await pablo.edit(f"**Download failed:** `{str(e)}`")

    caption = f"""**𝚃𝙸𝚃𝙻𝙴 :** [{thum}]({mo})\n**𝚁𝙴𝚀𝚄𝙴𝚂𝚃𝙴𝙳 𝙱𝚈 :** {message.from_user.mention}"""

    await client.send_video(
        message.chat.id,
        video=open(filename, "rb"),
        duration=int(info["duration"]),
        file_name=str(info["title"]),
        thumb=sedlyf if sedlyf else None,
        caption=caption,
        supports_streaming=True,
        reply_to_message_id=message.id
    )
    await pablo.delete()

    for f in (filename, sedlyf):
        if f and os.path.exists(f):
            os.remove(f)