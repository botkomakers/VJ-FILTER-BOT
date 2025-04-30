#brodcat_user



from pyrogram import Client, filters
from pyrogram.types import Message
from info import auth_users

@Client.on_message(filters.command("broadcast_user") & filters.user(auth_users))
async def broadcast_to_specific_user(bot: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply(
            "দয়া করে যে মেসেজটি পাঠাতে চান সেটিতে রিপ্লাই দিন এবং কমান্ডে ইউজার আইডি দিন।\n\nউদাহরণ:\n`/broadcast_user 123456789`"
        )

    try:
        args = message.text.strip().split()
        if len(args) < 2:
            return await message.reply("দয়া করে ইউজার আইডি দিন।\n\nউদাহরণ:\n`/broadcast_user 123456789`")

        user_id = int(args[1])

        target_msg = message.reply_to_message

        # ফরওয়ার্ডেড বা অন্য মেসেজের সমস্যা সামাল দিতে এখানে আলাদা হ্যান্ডেল
        if target_msg.forward_from_chat:
            from_chat_id = target_msg.forward_from_chat.id
            message_id = target_msg.forward_from_message_id
        else:
            from_chat_id = message.chat.id
            message_id = target_msg.id

        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )

        await message.reply(f"✅ মেসেজ ইউজার `{user_id}` কে পাঠানো হয়েছে।")

    except Exception as e:
        await message.reply(f"❌ মেসেজ পাঠানো যায়নি।\nকারণ: `{str(e)}`")


