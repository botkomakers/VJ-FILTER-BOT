import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002507577541  # Put your actual post channel ID here
ADMIN_ID = 7862181538  # Replace with your actual admin ID

def remove_usernames_from_title(title: str) -> str:
    # Regular expression to match '@username' or '@some_text'
    return re.sub(r'@[\w_]+', '', title).strip()  # Remove '@' followed by word characters or underscores

def replace_underscore_with_space(title: str) -> str:
    # Replace underscores with spaces if no underscore exists
    if "_" not in title:
        return title.replace("_", " ")  # Replace _ with a space
    return title

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()

    if not movies:
        await message.reply("тЭМ No movies found for today!")
        return

    # Building movie list with clickable titles
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)  # Remove username if any
        movie_title = replace_underscore_with_space(movie_title)  # Replace _ with space if no _ found

        # Make the movie title clickable by adding a link with movie_title
        movie_list += f"**{idx}.** [🎯 {movie_title}](tg://user?id={message.from_user.id})\n\n"  # This will allow the title to be clickable

    # Send the movie list as a reply
    await message.reply(
        f"**ЁЯУЕ Today's Movie List:**\n\n{movie_list}",
        quote=True
    )

@Client.on_message(filters.command("postlist"))
async def post_today_movies(client, message):
    # Fetch today's movies from your database
    movies = await get_today_movies()

    if not movies:
        await message.reply("тЭМ No movies available to post today!")
        return

    # Build the movie list with buttons
    movie_list = ""
    for idx, movie in enumerate(movies, start=1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)  # Remove username if any
        movie_title = replace_underscore_with_space(movie_title)  # Replace _ with space if no _ found

        # Make the movie title clickable by adding a link with movie_title
        movie_list += f"**{idx}.** [ЁЯОм {movie_title}](tg://user?id={message.from_user.id})\n\n"  # This will allow the title to be clickable

    # Inline buttons setup for action
    buttons = [
        [
            InlineKeyboardButton("Get Now", url="https://t.me/MovieDownload6G_bot"),  # Replace with actual movie link
            InlineKeyboardButton("Join Now", url="https://t.me/Movie_channel8")  # Replace with actual search link
        ]
    ]

    # Send the post message with inline buttons
    await client.send_message(
        POST_CHANNEL_ID,
        movie_list,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    # Clear today's movie list in the database
    await clear_today_movies()  # This will now work after implementation

    # Notify the admin
    await message.reply("тЬЕ Today's movie list has been cleared successfully!")