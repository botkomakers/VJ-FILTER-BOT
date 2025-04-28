import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002589776901  # Put your actual post channel ID here
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
        movie_list += f"**{idx}.** [ЁЯОм {movie_title}](tg://user?id={message.from_user.id})\n\n"  # This will allow the title to be clickable

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
            InlineKeyboardButton("Get Now", url="https://www.example.com/movie-link"),  # Replace with actual movie link
            InlineKeyboardButton("Search Now", url="https://www.example.com/search-now")  # Replace with actual search link
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















import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
ADMIN_ID = 7862181538  # ржЖржкржирж╛рж░ ржЖрж╕рж▓ ржЕрзНржпрж╛ржбржорж┐ржи ржЖржЗржбрж┐ ржжрж┐рзЯрзЗ ржкрж░рж┐ржмрж░рзНрждржи ржХрж░рзБржи
TMDB_API_KEY = "c3443ed2f96cd615e3badf6b68c8a689"  # Replace with your TMDB API key
POST_CHANNEL_ID = -1002589776901  # Your default post channel ID (you can change this)

def search_tmdb_movies(query: str):
    """Search TMDB API for movies and TV series based on the query."""
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    return response.json()

@Client.on_message(filters.command("post_movie_poster"))
async def post_movie_poster(client, message):
    # Extract the movie or series name from the command
    query = " ".join(message.command[1:])

    if not query:
        await message.reply("тЭМ Please provide a movie or series name!")
        return

    # Fetch the movies and series from TMDB API
    results = search_tmdb_movies(query)

    if not results.get('results'):
        await message.reply("тЭМ No movies or series found with that name!")
        return

    # Build a list of movie/series results
    buttons = []
    movie_list = "**Found Movies/Series:**\n\n"
    for idx, result in enumerate(results['results'], start=1):
        title = result['name'] if result.get('name') else result['title']
        poster_path = result.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster_url = "https://via.placeholder.com/500"  # Default image if no poster found

        # Adding button for each result
        movie_list += f"**{idx}.** {title}\n"
        buttons.append([InlineKeyboardButton(f"Post Now: {title}", callback_data=f"post_{idx}_{poster_url}_{title}")])

    # Send message with buttons to select movie/series to post
    await message.reply(
        movie_list,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^post_"))
async def handle_post_button(client, callback_query):
    # Extract movie/series details from callback data
    callback_data = callback_query.data.split("_")
    idx, poster_url, title = callback_data[1], callback_data[2], callback_data[3]

    # Ask the admin for the channel ID to post
    await callback_query.answer("Please provide the channel ID where you'd like to post the movie/series!")

    await callback_query.message.reply(
        f"ЁЯФ┤ **{title}**\n\nWould you like to post this movie/series with the poster below?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes, Post It!", callback_data=f"confirm_post_{idx}_{poster_url}_{title}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_post")]
        ])
    )

@Client.on_callback_query(filters.regex(r"^confirm_post_"))
async def confirm_post(client, callback_query):
    # Extract details from callback data
    callback_data = callback_query.data.split("_")
    idx, poster_url, title = callback_data[1], callback_data[2], callback_data[3]

    # Ask for the channel ID to post the movie
    await callback_query.answer("Please provide the channel ID where you'd like to post the movie/series!")

    # Ask the admin for the channel ID
    await callback_query.message.reply(
        f"Please provide the channel ID for posting **{title}**.\n\nYou can get the channel ID from the channel link (e.g., `@your_channel_name`)."
    )

@Client.on_message(filters.text & filters.user(ADMIN_ID))
async def post_to_channel(client, message):
    # Get the movie or series title
    if message.text.startswith("post_"):
        # Example: post_1_123456_some_movie_name
        data = message.text.split("_")
        idx, poster_url, title = data[1], data[2], data[3]

        # Post message in the channel with movie poster and Get Now button
        buttons = [
            [
                InlineKeyboardButton("Get Now", url=f"https://t.me/your_bot_link/{title}")
            ]
        ]

        try:
            await client.send_photo(
                POST_CHANNEL_ID,
                poster_url,
                caption=f"ЁЯОм **{title}**",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await message.reply(f"тЬЕ Movie/Series **{title}** has been successfully posted!")
        except FloodWait as e:
            await message.reply(f"тП│ Please wait {e.x} seconds before posting again.")

@Client.on_callback_query(filters.regex("cancel_post"))
async def cancel_post(client, callback_query):
    await callback_query.answer("Operation has been canceled.")
    await callback_query.message.delete()