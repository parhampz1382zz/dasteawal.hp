import asyncio
import feedparser
import google.generativeai as genai
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ─── تنظیمات ───
BOT_TOKEN = "8583286853:AAHl1Llj1i991t81RgyN22FuHplKJk8q61k"
CHANNEL_ID = "@dasteawal"
GEMINI_API_KEY = "AIzaSyAzuENCpZi2GUGLLcmKVHVRxj6Tsxkdw0w"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
last_news_id = None


def get_latest_news():
    """گرفتن خبر از RSS"""
    feed = feedparser.parse("https://www.tasnimnews.com/fa/rss/feed/0/8/0")
    
    if feed.entries:
        news = feed.entries[0]
        return {
            'id': news.get('id'),
            'title': news.get('title'),
            'summary': news.get('summary', '')
        }
    return None


def process_with_ai(title, summary):
    prompt = f"""
    این خبر رو بازنویسی کن برای کانال تلگرام.
    خلاصه و جذاب بنویس. حداکثر ۲ پاراگراف.
    
    عنوان: {title}
    خلاصه: {summary}
    
    فرمت:
    📰 [عنوان]
    
    [متن]
    """
    response = model.generate_content(prompt)
    return response.text


async def check_and_post():
    global last_news_id
    
    try:
        news = get_latest_news()
        
        if news:  # همیشه بفرسته (فقط برای تست)
            print(f"خبر جدید: {news['title']}")
            
            processed = process_with_ai(news['title'], news['summary'])
            await bot.send_message(CHANNEL_ID, processed)
            
            last_news_id = news['id']
            print("✅ ارسال شد!")
        else:
            print("خبر جدیدی نیست")
            
    except Exception as e:
        print(f"❌ خطا: {e}")


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_post, 'interval', minutes=1)
    scheduler.start()
    
    print("🤖 ربات شروع شد...")
    await check_and_post()
    
    while True:
        await asyncio.sleep(60)

asyncio.run(main())
