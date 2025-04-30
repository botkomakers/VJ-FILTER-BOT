# plugins/movie_listeners.py

from pyrogram import Client, filters
from database.today_movies_db import save_movie

LOG_CHANNEL_ID = -1002530980008  # তোমার লগ চ্যানেলের ID

@Client.on_message(filters.chat(LOG_CHANNEL_ID) & filters.video)
async def save_video_info(client, message):
    title = message.caption or message.video.file_name or "Untitled"
    await save_movie(title)