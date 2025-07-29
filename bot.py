import os
import json
import re
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8303642695:AAGs0HhQo2fGNTRRVIX4APFcHq7AbpstmlI"
OWNER_ID = 7383046042

FOOTER_FILE = "footer.json"

# Flask for uptime
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_flask).start()

bot = Client("media_caption_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Load footer from file
def load_footer():
    if not os.path.exists(FOOTER_FILE):
        return ""
    with open(FOOTER_FILE, "r") as f:
        return json.load(f).get("footer", "")

# Save footer to file
def save_footer(text):
    with open(FOOTER_FILE, "w") as f:
        json.dump({"footer": text}, f)

# Extract all links from a message
def extract_links(text):
    return re.findall(r'https?://\S+', text)

@bot.on_message(filters.private & filters.command("setfooter") & filters.user(OWNER_ID))
async def set_footer(_, message: Message):
    if len(message.text.split(" ", 1)) < 2:
        return await message.reply("⚠️ ব্যবহার: /setfooter <footer text>")
    footer_text = message.text.split(" ", 1)[1]
    save_footer(footer_text)
    await message.reply("✅ নতুন ফুটার সংরক্ষণ করা হয়েছে।")

@bot.on_message(filters.private & filters.command("removefooter") & filters.user(OWNER_ID))
async def remove_footer(_, message: Message):
    save_footer("")
    await message.reply("❌ ফুটার মুছে ফেলা হয়েছে।")

@bot.on_message(filters.private & filters.command("viewfooter") & filters.user(OWNER_ID))
async def view_footer(_, message: Message):
    footer = load_footer()
    if footer:
        await message.reply(f"📌 বর্তমান ফুটার:\n\n{footer}")
    else:
        await message.reply("ℹ️ কোনো ফুটার সেট করা নেই।")

@bot.on_message(filters.private & filters.user(OWNER_ID) & (filters.photo | filters.video))
async def media_handler(client, message: Message):
    if not message.caption:
        return await message.reply("❌ লিংক সহ ক্যাপশন দিন!")

    links = extract_links(message.caption)
    if not links:
        return await message.reply("❌ কোনো লিংক পাওয়া যায়নি ক্যাপশনে!")

    formatted_links = "\n".join([f"Video {i+1}. 👉 {link}" for i, link in enumerate(links)])
    footer_text = load_footer()
    final_caption = f"""📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐋𝐢𝐧𝐤𝐬/👀𝐖𝐚𝐭𝐜𝐡 𝐎𝐧𝐥𝐢𝐧𝐞
{formatted_links}
{footer_text}"""

    if message.photo:
        await message.reply_photo(photo=message.photo.file_id, caption=final_caption)
    elif message.video:
        await message.reply_video(video=message.video.file_id, caption=final_caption)

print("Bot is starting...")
bot.run()
