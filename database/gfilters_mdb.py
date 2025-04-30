
import pymongo
from info import OTHER_DB_URI, DATABASE_NAME
from pyrogram import enums
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)







myclient = pymongo.MongoClient(OTHER_DB_URI)
mydb = myclient[DATABASE_NAME]



async def add_gfilter(gfilters, text, reply_text, btn, file, alert):
    mycol = mydb[str(gfilters)]
    # mycol.create_index([('text', 'text')])

    data = {
        'text':str(text),
        'reply':str(reply_text),
        'btn':str(btn),
        'file':str(file),
        'alert':str(alert)
    }

    try:
        mycol.update_one({'text': str(text)},  {"$set": data}, upsert=True)
    except:
        logger.exception('Some error occured!', exc_info=True)


async def find_gfilter(gfilters, name):
    mycol = mydb[str(gfilters)]

    query = mycol.find( {"text":name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except:
                alert = None
        return reply_text, btn, alert, fileid
    except:
        return None, None, None, None


async def get_gfilters(gfilters):
    mycol = mydb[str(gfilters)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file['text']
            texts.append(text)
    except:
        pass
    return texts


async def delete_gfilter(message, text, gfilters):
    mycol = mydb[str(gfilters)]

    myquery = {'text':text }
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that gfilter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that gfilter!", quote=True)

async def del_allg(message, gfilters):
    if str(gfilters) not in mydb.list_collection_names():
        await message.edit_text("Nothing to Remove !")
        return

    mycol = mydb[str(gfilters)]
    try:
        mycol.drop()
        await message.edit_text(f"All gfilters has been removed !")
    except:
        await message.edit_text("Couldn't remove all gfilters !")
        return

async def count_gfilters(gfilters):
    mycol = mydb[str(gfilters)]

    count = mycol.count()
    return False if count == 0 else count


async def gfilter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount += count

    totalcollections = len(collections)

    return totalcollections, totalcount



from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
requests_col = db["pending_requests"]

# ✅ মুভি রিকোয়েস্ট অ্যাড
async def add_movie_request(user_id, movie_name):
    await requests_col.insert_one({
        "user_id": user_id,
        "movie_name": movie_name
    })

# ✅ মুভি রিকোয়েস্ট ডিলিট (user_id + movie_name দিয়ে)
async def delete_movie_request(user_id, movie_name):
    await requests_col.delete_one({
        "user_id": user_id,
        "movie_name": movie_name
    })

# ✅ সব মুভি রিকোয়েস্ট বের করা
async def get_all_requests():
    return await requests_col.find().to_list(length=100)

# ✅ সব রিকোয়েস্ট ক্লিয়ার করা
async def clear_all_requests():
    await requests_col.delete_many({})




# Add Voting Entry
async def add_vote_request(user_id, movie_name, message_id):
    data = {
        "user_id": user_id,
        "movie_name": movie_name,
        "votes": 0,
        "voters": [],
        "message_id": message_id
    }
    await requests_col.insert_one(data)

# Vote on Request
async def vote_request(message_id, user_id, vote_type):
    req = await requests_col.find_one({"message_id": message_id})
    if not req:
        return False

    if user_id in req.get("voters", []):
        return "already_voted"

    update_query = {
        "$inc": {"votes": 1},
        "$push": {"voters": user_id}
    }
    await requests_col.update_one({"message_id": message_id}, update_query)
    return "voted"

# Get Top Requests
async def get_top_voted_requests(limit=10):
    cursor = requests_col.find().sort("votes", -1).limit(limit)
    return [doc async for doc in cursor]