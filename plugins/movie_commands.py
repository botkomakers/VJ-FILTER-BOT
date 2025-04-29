import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002458764661
ADMIN_ID = 7862181538
POST_IMAGE_URL = "https://i.ibb.co/21RKmKDG/file-1485.jpg"

MOVIES_PER_PAGE = 5  # প্রতি পেজে ৫টা মুভি দেখাবে

def remove_usernames_from_title(title: str) -> str:
    return re.sub(r'@[\w_]+', '', title).strip()

def replace_underscore_with_space(title: str) -> str:
    return title.replace("_", " ")

def remove_extra_words_from_title(title: str) -> str:
    patterns = [
        r"\.mkv", r"\.mp4", r"\.avi", r"\.web-dl", r"\.webrip", r"\.hdrip",
        r"\.bluray", r"\.1080p", r"\.720p", r"\.480p", r".*?", r".*?"
    ]
    for pattern in patterns:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    return title.strip()

def clean_title(title: str) -> str:
    title = remove_usernames_from_title(title)
    title = replace_underscore_with_space(title)
    title = remove_extra_words_from_title(title)
    return title

def create_movie_list(movies, page=0):
    start = page * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    movie_list = ""
    for idx, movie in enumerate(movies[start:end], start=start+1):
        movie_title = clean_title(movie['title'])
        movie_list += f"**{idx}.** 🎯 ` {movie_title} `\n\n"
    return movie_list

def get_buttons(total_movies, current_page):
    total_pages = (total_movies + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE
    buttons = []

    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_page}"))
    if (current_page + 1) < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_page}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton("🎬 Get Now", url="https://t.me/MovieDownload6G_bot"),
        InlineKeyboardButton("🎯 Join Now", url="https://t.me/Movie_channel8")
    ])

    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("listtoday"))
async def list_today_movies(client, message):
    movies = await get_today_movies()

    if not movies:
        await message.reply("🚫 No movies found for today!")
        return

    movie_list = create_movie_list(movies)

    await message.reply(
        f"**🎉 Today's Movie List:**\n\n{movie_list}",
        quote=True
    )

@Client.on_message(filters.command("postlist") & filters.user(ADMIN_ID))
async def post_today_movies(client, message):
    movies = await get_today_movies()

    if not movies:
        await message.reply("🚫 No movies available to post today!")
        return

    movie_list = create_movie_list(movies, page=0)
    reply_markup = get_buttons(len(movies), current_page=0)

    await client.send_photo(
        POST_CHANNEL_ID,
        photo=POST_IMAGE_URL,
        caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
        reply_markup=reply_markup
    )

    await message.reply("✅ Movie list has been successfully posted to the channel!")

@Client.on_callback_query(filters.regex("^(next|prev)_"))
async def paginate_movies(client, callback_query):
    data = callback_query.data
    action, page = data.split("_")
    page = int(page)

    if action == "next":
        new_page = page + 1
    else:
        new_page = page - 1

    movies = await get_today_movies()

    if not movies:
        await callback_query.answer("No movies available!", show_alert=True)
        return

    if new_page < 0 or new_page * MOVIES_PER_PAGE >= len(movies):
        await callback_query.answer("No more movies!", show_alert=True)
        return

    movie_list = create_movie_list(movies, page=new_page)
    reply_markup = get_buttons(len(movies), current_page=new_page)

    try:
        await callback_query.message.edit_caption(
            caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
            reply_markup=reply_markup
        )
    except Exception as e:
        await callback_query.answer(f"Error: {e}", show_alert=True)

@Client.on_message(filters.command("clear_today_list") & filters.user(ADMIN_ID))
async def clear_today_movie_list(client, message):
    await clear_today_movies()
    await message.reply("✅ Today's movie list has been cleared successfully!")