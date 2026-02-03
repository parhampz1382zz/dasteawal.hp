import asyncio
import os
from aiogram import Bot

TELE_TOKEN = os.getenv("8583286853:AAHl1Llj1i991t81RgyN22FuHplKJk8q61k")
CHAT_ID = "@dasteawal"

async def send_message():
    bot = Bot(token=TELE_TOKEN)
    try:
        await bot.send_message(CHAT_ID, "سلام! بات داره کار میکنه 🎉")
        print("✅ پیام ارسال شد!")
    except Exception as e:
        print(f"❌ خطا: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(send_message())
