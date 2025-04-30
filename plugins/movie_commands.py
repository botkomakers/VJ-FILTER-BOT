import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database.today_movies_db import get_today_movies, clear_today_movies

POST_CHANNEL_ID = -1002507577541  # Your post channel ID
ADMIN_ID = 7862181538  # Your admin ID
POST_IMAGE_URL = "https://i.ibb.co/21RKmKDG/file-1485.jpg"  # Image URL to post

MOVIES_PER_PAGE = 5  # প্রতি পেজে ৫ টা মুভি দেখাবে

def remove_usernames_from_title(title: str) -> str:
    return re.sub(r'@[\w_]+', '', title).strip()

def replace_underscore_with_space(title: str) -> str:
    return title.replace("_", " ")

def create_movie_list(movies, page=0):
    start = page * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    movie_list = ""
    for idx, movie in enumerate(movies[start:end], start=start+1):
        movie_title = movie['title']
        movie_title = remove_usernames_from_title(movie_title)
        movie_title = replace_underscore_with_space(movie_title)
        movie_list += f"**{idx}.** 🎯 ` {movie_title} `\n\n"  # Monotext format
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

    # Always add "Get Now" button at the bottom
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

    # Send the message with photo in channel
    sent_message = await client.send_photo(
        POST_CHANNEL_ID,
        photo=POST_IMAGE_URL,
        caption=f"**🎉 Today's Movie List:**\n\n{movie_list}",
        reply_markup=reply_markup
    )

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

    # Edit message
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



































#request_ms

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.gfilters_mdb import add_movie_request, delete_movie_request, get_all_requests, clear_all_requests
from helper.tmdb import search_movie, get_movie_details
from datetime import datetime
from info import ADMIN_IDS, LOG_CHANNEL, MAX_REQUESTS_PER_DAY, REQUEST_EXPIRE_DAYS

# ইউজার রিকোয়েস্ট হ্যান্ডলার
@Client.on_message(filters.command("requestbot") & filters.private)
async def handle_request(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/requestbot Movie Name`", quote=True)

    movie_name = " ".join(message.command[1:])
    user = message.from_user

    # TMDb দিয়ে মুভি সার্চ
    search_results = await search_movie(movie_name)

    if not search_results:
        return await message.reply(
            f"❌ No movie found with the name `{movie_name}`.\nPlease check the spelling and try again.",
            quote=True
        )

    # সবচেয়ে কাছাকাছি রেজাল্ট বের করো
    top_result = search_results[0]
    confirmed_movie_name = top_result.get("title")
    poster_path = top_result.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    # যদি পুরোপুরি মিলে না, সাজেশন দাও
    if confirmed_movie_name.lower() != movie_name.lower():
        suggestions = "\n".join(
            [f"`{movie.get('title')}` ({movie.get('release_date', 'N/A')[:4]})" for movie in search_results[:5]]
        )
        return await message.reply(
            f"❗ Did you mean one of these?\n\n{suggestions}\n\n"
            "Please send the exact movie name again using `/requestbots` command.",
            quote=True
        )

    # ডেটাবেজে রিকোয়েস্ট সেভ করো
    await add_movie_request(user.id, confirmed_movie_name)

    # অ্যাডমিনদের কাছে রিকোয়েস্ট পাঠাও
    await send_movie_request_to_admins(client, confirmed_movie_name, user.id, user.first_name, poster_url)

    await message.reply(
        f"✅ Your request for `{confirmed_movie_name}` has been successfully submitted!\n"
        "We will notify you once it's available.\n\n"
        "__Thanks for using our service! Stay tuned!__",
        quote=True
    )

# অ্যাডমিনদের কাছে রিকোয়েস্ট পাঠানোর ফাংশন
async def send_movie_request_to_admins(client: Client, movie_name: str, user_id: int, user_name: str, poster_url: str = None):
    request_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    caption = f"""
📩 **New Movie Request Received!**

🎬 **Movie:** `{movie_name}`
👤 **Requested By:** [{user_name}](tg://user?id={user_id})
🆔 **User ID:** `{user_id}`
🕰️ **Requested At:** `{request_time}`

📣 _Please Approve or Reject the request from below._
"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_{movie_name}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_{movie_name}")
        ]
    ])

    # Send to LOG_CHANNEL + all admins
    target_chats = set([LOG_CHANNEL] + ADMIN_IDS)

    for chat_id in target_chats:
        try:
            if poster_url:
                await client.send_photo(
                    chat_id=chat_id,
                    photo=poster_url,
                    caption=caption,
                    reply_markup=buttons
                )
            else:
                await client.send_message(
                    chat_id=chat_id,
                    text=caption,
                    reply_markup=buttons
                )
        except Exception as e:
            print(f"Failed to send request to {chat_id}: {e}")

# Approve/Reject বাটন হ্যান্ডলার
@Client.on_callback_query(filters.regex(r"^(approve|reject)_(\d+)_(.+)"))
async def approve_or_reject_request(client: Client, callback_query: CallbackQuery):
    action, user_id, movie_name = callback_query.data.split("_", 2)
    user_id = int(user_id)

    if callback_query.from_user.id not in ADMIN_IDS:
        return await callback_query.answer("❌ You are not authorized to perform this action.", show_alert=True)

    movie_details = await get_movie_details(movie_name)
    poster_url = f"https://image.tmdb.org/t/p/w500{movie_details.get('poster_path')}" if movie_details and movie_details.get("poster_path") else None
    overview = movie_details.get("overview", "No description available.") if movie_details else "No description available."

    status_text = (
        "**Congratulations!**\n\n✅ Your requested movie has been **Accepted** and will be uploaded shortly. Stay connected!"
        if action == "approve"
        else "**Oops!**\n\n❌ Unfortunately, your requested movie has been **Rejected**. We apologize for the inconvenience."
    )

    caption = f"""
🎬 **{movie_name}**
📝 **Description:** {overview[:400]}...

{status_text}

__Thanks for understanding!__
"""

    try:
        if poster_url:
            await client.send_photo(user_id, poster_url, caption=caption)
        else:
            await client.send_message(user_id, caption)
    except Exception as e:
        print(f"❗ Failed to notify user {user_id}: {e}")

    # ডেটাবেজ থেকে রিকোয়েস্ট মুছে ফেলো
    await delete_movie_request(user_id, movie_name)

    # মেসেজ আপডেট করো
    new_caption = (
        f"✅ Approved!\n\n🎬 `{movie_name}`\n👤 [User](tg://user?id={user_id})"
        if action == "approve"
        else f"❌ Rejected!\n\n🎬 `{movie_name}`\n👤 [User](tg://user?id={user_id})"
    )

    try:
        await callback_query.message.edit_caption(caption=new_caption)
    except Exception as e:
        print(f"❗ Failed to edit admin message: {e}")

    await callback_query.answer(f"Request {action.title()}ed!", show_alert=True)

# রিকোয়েস্ট লিস্ট দেখানোর কমান্ড
@Client.on_message(filters.command("requestlist") & filters.user(ADMIN_IDS))
async def request_list(client: Client, message: Message):
    data = await get_all_requests()
    if not data:
        return await message.reply("📭 No pending movie requests.")

    text = "🎞️ **Pending Movie Requests:**\n\n"
    for i, req in enumerate(data, start=1):
        requested_at = req.get("requested_at", "N/A")
        text += f"{i}. `{req['movie_name']}` - [User](tg://user?id={req['user_id']}) (🕰️ {requested_at})\n"

    await message.reply(text)

# সব রিকোয়েস্ট ক্লিয়ার করার কমান্ড
@Client.on_message(filters.command("clearrequests") & filters.user(ADMIN_IDS))
async def clear_requests(client: Client, message: Message):
    await clear_all_requests()
    await message.reply("✅ All pending movie requests have been cleared.")

# ইউজার নিজে নিজের রিকোয়েস্ট বাতিল করতে পারবে
@Client.on_message(filters.command("cancelrequest") & filters.private)
async def cancel_request(client: Client, message: Message):
    user = message.from_user
    movie_name = " ".join(message.command[1:]) if len(message.command) > 1 else None

    if not movie_name:
        return await message.reply("❌ Usage: `/cancelrequest Movie Name`", quote=True)

    try:
        await delete_movie_request(user.id, movie_name)
        await message.reply(f"✅ Your request for `{movie_name}` has been cancelled successfully!\n\n__Feel free to request again anytime!__", quote=True)
    except Exception as e:
        await message.reply(f"❌ Failed to cancel request: {e}", quote=True) 







