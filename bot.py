import os
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8303642695:AAGs0HhQo2fGNTRRVIX4APFcHq7AbpstmlI"
OWNER_ID = 7383046042

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

Thread(target=run_flask).start()

bot = Client("media_caption_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

FOOTER_TEMPLATE = """
📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐋𝐢𝐧𝐤𝐬/👀𝐖𝐚𝐭𝐜𝐡 𝐎𝐧𝐥𝐢𝐧𝐞
Video 1. 👉 {link}
🍀Backup & All Channel Link🔗👇
https://t.me/+lFelFNR1D6NjMjc1 ✅
"""

@bot.on_message(filters.private & filters.user(OWNER_ID) & (filters.video | filters.photo))
async def handle_media(client, message: Message):
    if not message.caption:
        await message.reply_text("❌ লিংক সহ ক্যাপশন দিন!")
        return

    # লিংক খুঁজে বের করো ক্যাপশন থেকে
    words = message.caption.split()
    link = next((w for w in words if w.startswith("http")), None)

    if not link:
        await message.reply_text("❌ কোনো লিংক পাওয়া যায়নি ক্যাপশনে!")
        return

    footer = FOOTER_TEMPLATE.format(link=link)

    if message.photo:
        await message.reply_photo(photo=message.photo.file_id, caption=footer)
    elif message.video:
        await message.reply_video(video=message.video.file_id, caption=footer)

print("Bot is starting...")
bot.run()
