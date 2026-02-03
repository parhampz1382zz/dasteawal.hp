import asyncio
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ─── تنظیمات ───
BOT_TOKEN = "8583286853:AAHl1Llj1i991t81RgyN22FuHplKJk8q61k"
CHANNEL_ID = "@dasteawal"  # یا آیدی عددی
GEMINI_API_KEY = "AIzaSyAzuENCpZi2GUGLLcmKVHVRxj6Tsxkdw0w"

# تنظیم Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)

# ذخیره آخرین خبر برای جلوگیری از تکرار
last_news_url = None


def get_latest_news():
    """گرفتن آخرین خبر از ایسنا"""
    url = "https://www.isna.ir/latest-news"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # پیدا کردن اولین خبر
    news_item = soup.select_one('.items li a')
    
    if news_item:
        news_url = "https://www.isna.ir" + news_item.get('href')
        return news_url
    return None


def get_news_content(url):
    """گرفتن محتوای کامل خبر"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    title = soup.select_one('h1.first-title')
    title = title.text.strip() if title else ""
    
    body = soup.select_one('.item-body')
    body = body.text.strip() if body else ""
    
    return title, body


def process_with_ai(title, body):
    """پردازش خبر با Gemini"""
    prompt = f"""
    این خبر رو بازنویسی کن و خلاصه‌تر بنویس برای کانال تلگرام.
    لحن رسمی و خبری باشه. حداکثر ۳ پاراگراف.
    
    عنوان: {title}
    متن: {body}
    
    فرمت خروجی:
    📰 [عنوان جذاب]
    
    [متن خلاصه شده]
    """
    
    response = model.generate_content(prompt)
    return response.text


async def check_and_post():
    """چک کردن خبر جدید و ارسال"""
    global last_news_url
    
    try:
        news_url = get_latest_news()
        
        if news_url and news_url != last_news_url:
            print(f"خبر جدید: {news_url}")
            
            title, body = get_news_content(news_url)
            
            if title and body:
                processed_news = process_with_ai(title, body)
                
                # اضافه کردن لینک منبع
                final_text = f"{processed_news}\n\n🔗 منبع: ایسنا"
                
                await bot.send_message(CHANNEL_ID, final_text)
                last_news_url = news_url
                print("✅ خبر ارسال شد!")
        else:
            print("خبر جدیدی نیست")
            
    except Exception as e:
        print(f"❌ خطا: {e}")


async def main():
    scheduler = AsyncIOScheduler()
    
    # هر ۵ دقیقه چک کن
    scheduler.add_job(check_and_post, 'interval', minutes=1)
    scheduler.start()
    
    print("🤖 ربات شروع به کار کرد...")
    
    # اجرای اولیه
    await check_and_post()
    
    # زنده نگه داشتن
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
