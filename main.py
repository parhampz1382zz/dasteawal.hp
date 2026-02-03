import asyncio
import httpx
from bs4 import BeautifulSoup
import google.generativeai as genai
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ─── تنظیمات ───
BOT_TOKEN = "8583286853:AAHl1Llj1i991t81RgyN22FuHplKJk8q61k"
CHANNEL_ID = "@dasteawal"
GEMINI_API_KEY = "AIzaSyAzuENCpZi2GUGLLcmKVHVRxj6Tsxkdw0w"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

bot = Bot(token=BOT_TOKEN)
sent_urls = set()  # خبرهای ارسال شده
news_queue = []    # صف خبرها


async def get_news_from_site():
    """گرفتن خبرها از صفحه اول BBC فارسی"""
    async with httpx.AsyncClient() as client:
        r = await client.get("https://www.bbc.com/persian", timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        news_list = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            if '/persian/articles/' in href and len(title) > 20:
                full_url = href if href.startswith('http') else f"https://www.bbc.com{href}"
                if full_url not in sent_urls:
                    news_list.append({'title': title, 'url': full_url})
        
        # حذف تکراری
        seen = set()
        unique = []
        for n in news_list:
            if n['url'] not in seen:
                seen.add(n['url'])
                unique.append(n)
        
        return unique[:15]  # ۱۵ خبر اول


async def rewrite_news(title):
    prompt = f"این عنوان خبر رو جذاب‌تر بنویس (فقط یک جمله): {title}"
    response = model.generate_content(prompt)
    return response.text.strip()


async def post_one_news():
    global news_queue
    
    try:
        # اگه صف خالیه، دوباره بگیر
        if not news_queue:
            print("🔄 گرفتن خبرهای جدید...")
            news_queue = await get_news_from_site()
            print(f"📊 {len(news_queue)} خبر پیدا شد")
        
        if news_queue:
            news = news_queue.pop(0)
            print(f"📰 {news['title'][:40]}...")
            
            text = await rewrite_news(news['title'])
            message = f"{text}\n\n🔗 {news['url']}"
            
            await bot.send_message(CHANNEL_ID, message)
            sent_urls.add(news['url'])
            print("✅ ارسال شد!")
        else:
            print("⏳ خبر جدیدی نیست")
            
    except Exception as e:
        print(f"❌ خطا: {e}")


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(post_one_news, 'interval', minutes=1)
    scheduler.start()
    
    print("🤖 ربات شروع شد!")
    await post_one_news()
    
    while True:
        await asyncio.sleep(60)

asyncio.run(main())
