from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import LOG_CHANNEL  # LOG_CHANNEL import করা হয়েছে info.py থেকে

# ইউজার যখন /requestbot লিখবে
@Client.on_message(filters.command("requestbot") & filters.private)
async def handle_request(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: `/requestbot movie name`", quote=True)

    movie_name = " ".join(message.command[1:])
    user = message.from_user

    text = f"**নতুন মুভি অনুরোধ এসেছে:**\n\n**🎬 মুভি:** `{movie_name}`\n**👤 অনুরোধ করেছে:** [{user.first_name}](tg://user?id={user.id})"

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Already Uploaded", callback_data=f"uploaded_{user.id}"),
            InlineKeyboardButton("⬆️ Upload Soon", callback_data=f"uploading_{user.id}"),
            InlineKeyboardButton("⛔ Can't Upload", callback_data=f"cantupload_{user.id}")
        ]
    ])

    await client.send_message(
        chat_id=LOG_CHANNEL,
        text=text,
        reply_markup=buttons
    )

    await message.reply("✅ অনুরোধটি সফলভাবে পাঠানো হয়েছে!", quote=True)


# ইনলাইন বাটনে ক্লিক করলে কী হবে
@Client.on_callback_query(filters.regex(r"^(uploaded|uploading|cantupload)_(\d+)$"))
async def handle_status_reply(client, callback_query):
    action, user_id = callback_query.data.split("_")
    user_id = int(user_id)

    status_map = {
        "uploaded": "✅ মুভিটি ইতিমধ্যেই আপলোড করা হয়েছে!",
        "uploading": "⬆️ শীঘ্রই মুভিটি আপলোড করা হবে!",
        "cantupload": "⛔ দুঃখিত, মুভিটি আপলোড করা সম্ভব নয়।"
    }

    await callback_query.answer("স্ট্যাটাস পাঠানো হলো", show_alert=False)

    try:
        await client.send_message(user_id, status_map[action])
    except:
        pass

    await callback_query.edit_message_reply_markup(reply_markup=None)