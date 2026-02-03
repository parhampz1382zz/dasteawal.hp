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


async def rewrite_news(title, summary):
    prompt = f"""این خبر رو بازنویسی کن:
عنوان: {title}
خلاصه: {summary}

فقط متن خبر رو بنویس، کوتاه و جذاب."""
    
    response = model.generate_content(prompt)
    return response.text


async def check_and_post():
    try:
        print("🔄 در حال گرفتن RSS...")
        
        feed = feedparser.parse("https://feeds.bbcpersian.com/feeds/rss/persian/iran/rss.xml")
        
        print(f"📊 تعداد خبر: {len(feed.entries)}")
        
        if feed.entries:
            news = feed.entries[0]
            title = news.get('title', '')
            summary = news.get('summary', '')
            
            print(f"📰 عنوان: {title}")
            
            print("🤖 در حال بازنویسی با AI...")
            text = await rewrite_news(title, summary)
            
            print(f"✍️ متن AI: {text[:50]}...")
            
            await bot.send_message(CHANNEL_ID, text)
            print("✅ ارسال شد!")
        else:
            print("❌ هیچ خبری در RSS نیست")
            
    except Exception as e:
        print(f"❌ خطا: {type(e).__name__}: {e}")


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_post, 'interval', minutes=1)
    scheduler.start()
    
    print("🤖 ربات شروع شد...")
    await check_and_post()
    
    while True:
        await asyncio.sleep(60)

asyncio.run(main())
