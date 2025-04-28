from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from info import DB_URL, DB_NAME

# MongoDB client setup
client = AsyncIOMotorClient(DB_URL)
db = client[DB_NAME]
movie_list_col = db.today_movie_list

# Save a new movie to the database
async def save_movie(title: str):
    now = datetime.utcnow()
    twelve_hours_ago = now - timedelta(hours=12)

    # Check if the same movie was saved within the last 12 hours
    existing = await movie_list_col.find_one({
        "title": title,
        "time": {"$gte": twelve_hours_ago}
    })

    if not existing:
        await movie_list_col.insert_one({
            "title": title,
            "time": now
        })

# Get today's movies (within the last 24 hours)
async def get_today_movies():
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    movies = await movie_list_col.find({"time": {"$gte": yesterday}}).to_list(length=100)
    return movies

# Clear all movies added today
async def clear_today_movies():
    now = datetime.utcnow()
    yesterday = now - timedelta(hours=24)
    await movie_list_col.delete_many({"time": {"$gte": yesterday}})

# Clear all movies from the database
async def clear_all_movies():
    await movie_list_col.delete_many({})












#unikelinpk

