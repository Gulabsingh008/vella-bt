import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from imdb import IMDb
from playwright.sync_api import sync_playwright

# ✅ Config
BOT_TOKEN = "7982548340:AAEfUijD-WP8bw3TYydGyoZqPYGRmKWrGK8"
TMDB_API_KEY = "7982548340:AAEfUijD-WP8bw3TYydGyoZqPYGRmKWrGK8"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ✅ TMDB Poster
def get_tmdb_poster(url):
    match = re.search(r'/movie/(\d+)', url)
    if not match:
        return None
    movie_id = match.group(1)
    tmdb_api = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    res = requests.get(tmdb_api).json()
    if 'poster_path' in res:
        return f"https://image.tmdb.org/t/p/w500{res['poster_path']}"
    return None

# ✅ IMDb Poster
def get_imdb_poster(url):
    match = re.search(r'/title/(tt\d+)', url)
    if not match:
        return None
    movie_id = match.group(1)
    ia = IMDb()
    movie = ia.get_movie(movie_id[2:])
    return movie.get('cover url')

# ✅ Netflix Thumbnail via Screenshot
def get_netflix_poster(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(5000)
            path = "netflix_poster.png"
            page.screenshot(path=path, full_page=True)
            browser.close()
            return path
    except Exception as e:
        print(f"Netflix error: {e}")
        return None

# ✅ ZEE5 Thumbnail via Screenshot (same as Netflix)
def get_zee5_poster(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(5000)
            path = "zee5_poster.png"
            page.screenshot(path=path, full_page=True)
            browser.close()
            return path
    except Exception as e:
        print(f"ZEE5 error: {e}")
        return None

# ✅ Start Command
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("Send me a link from TMDB, IMDb, Netflix, or ZEE5 to get poster 📸")

# ✅ Link Handler
@dp.message_handler()
async def handle_link(message: types.Message):
    url = message.text.strip()
    poster = None

    if "themoviedb.org" in url:
        poster = get_tmdb_poster(url)
    elif "imdb.com" in url:
        poster = get_imdb_poster(url)
    elif "netflix.com" in url:
        poster = get_netflix_poster(url)
    elif "zee5.com" in url:
        poster = get_zee5_poster(url)
    else:
        await message.reply("❌ Unsupported link. Please send TMDB, IMDb, Netflix or ZEE5 link.")
        return

    if poster:
        if poster.endswith(".png") or poster.endswith(".jpg"):
            await message.reply_photo(open(poster, 'rb'))
        else:
            await message.reply_photo(poster)
    else:
        await message.reply("⚠️ Poster not found or failed to fetch.")

# ✅ Run bot
if __name__ == "__main__":
    executor.start_polling(dp)
