#make by siam








# plugins/backdrop.py

import requests
import random
from pyrogram import Client, filters
from info import TMDB_API_KEY

TMDB_RANDOM_MOVIE_API = "https://api.themoviedb.org/3/discover/movie"
TMDB_RANDOM_TV_API = "https://api.themoviedb.org/3/discover/tv"
IMAGE_PATH = "https://image.tmdb.org/t/p/original"

@app.on_message(filters.command("backdrop") & filters.private)
async def random_backdrop(client, message):
    try:
        # Movie অথবা TV থেকে যেকোনো একটা রেনডমলি নেব
        endpoint = random.choice([TMDB_RANDOM_MOVIE_API, TMDB_RANDOM_TV_API])

        params = {
            "api_key": TMDB_API_KEY,
            "sort_by": "popularity.desc",
            "page": random.randint(1, 500),  # যেকোনো পেজ রেনডম
        }
        response = requests.get(endpoint, params=params)
        data = response.json()

        results = data.get("results")
        if not results:
            return await message.reply_text("কিছু খুঁজে পাওয়া যায়নি, আবার চেষ্টা করুন!", quote=True)
        
        movie = random.choice(results)
        backdrop_path = movie.get("backdrop_path")

        if not backdrop_path:
            return await message.reply_text("ব্যাকড্রপ ইমেজ পাওয়া যায়নি, আবার চেষ্টা করুন!", quote=True)

        title = movie.get('title') or movie.get('name') or "Unknown Title"
        release_date = movie.get('release_date') or movie.get('first_air_date') or "Unknown Date"
        backdrop_url = IMAGE_PATH + backdrop_path

        await message.reply_photo(
            photo=backdrop_url,
            caption=f"**শিরোনাম:** {title}\n**তারিখ:** {release_date}",
        )
    except Exception as e:
        await message.reply_text(f"ভুল হয়েছে: {e}", quote=True)