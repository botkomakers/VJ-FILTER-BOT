import aiohttp

TMDB_API_KEY = "c3443ed2f96cd615e3badf6b68c8a689"  # অবশ্যই তোমার TMDB API KEY বসাও!

# মুভি সার্চ
async def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("results", [])
            else:
                return []

# নির্দিষ্ট মুভির ডিটেলস
async def get_movie_details(name):
    results = await search_movie(name)
    if results:
        return results[0]
    else:
        return None
