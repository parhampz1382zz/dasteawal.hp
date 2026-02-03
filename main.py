import asyncio
import os
from aiogram import Bot

TOKEN = os.environ.get("TELE_TOKEN")
CHAT_ID = "@dasteawal"

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(CHAT_ID, "سلام! بات داره کار میکنه 🎉")
    await bot.session.close()
    print("Done!")

asyncio.run(main())
