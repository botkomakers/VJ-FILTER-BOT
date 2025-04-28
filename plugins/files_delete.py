from pyrogram import Client, filters
from info import DELETE_CHANNELS
from database.ia_filterdb import col, sec_col, unpack_new_file_id
import re, logging
import asyncio

logger = logging.getLogger(__name__)
media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    try:
        # Step 1: Processing শুরু
        processing = await message.reply_text("⏳ Processing your request...")

        # Step 2: মিডিয়া চেক
        media = None
        for file_type in ("document", "video", "audio"):
            media = getattr(message, file_type, None)
            if media:
                break

        if not media:
            await processing.edit("❌ No valid media found.")
            return

        # Step 3: Searching Database
        await asyncio.sleep(0.5)  # একটু টাইম ডিলে
        await processing.edit("🔍 Searching database for the file...")

        # unpack file_id
        try:
            file_id, file_ref = unpack_new_file_id(media.file_id)
        except Exception as e:
            logger.error(f"Error in unpack_new_file_id: {e}")
            await processing.edit("❌ Error processing file ID.")
            return

        # প্রথম ট্রাই: file_id দিয়ে ডিলিট
        result = col.delete_one({'file_id': file_id})
        if not result.deleted_count:
            result = sec_col.delete_one({'file_id': file_id})

        if result.deleted_count:
            logger.info('File successfully deleted by file_id.')
            await asyncio.sleep(0.5)
            await processing.edit("✅ File successfully deleted!")
            return

        # দ্বিতীয় ট্রাই: file_name+size দিয়ে ডিলিট
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        unwanted_chars = ['[', ']', '(', ')']
        for char in unwanted_chars:
            file_name = file_name.replace(char, '')
        file_name = ' '.join(filter(lambda x: not x.startswith('@'), file_name.split()))

        result = col.delete_many({
            'file_name': file_name,
            'file_size': media.file_size
        })
        if not result.deleted_count:
            result = sec_col.delete_many({
                'file_name': file_name,
                'file_size': media.file_size
            })

        if result.deleted_count:
            logger.info('File successfully deleted by file_name and size.')
            await asyncio.sleep(0.5)
            await processing.edit("✅ File successfully deleted (by name matching)!")
        else:
            logger.info('File not found in database.')
            await asyncio.sleep(0.5)
            await processing.edit("❌ File not found in database.")

    except Exception as error:
        logger.error(f"Unexpected error: {error}")
        await message.reply_text(f"❌ Unexpected error occurred.\n\n{error}")