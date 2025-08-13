import os
import json
import re
import string
import random
from flask import Flask, render_template_string
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = 22134923
API_HASH = "d3e9d2f01d3291e87ea65298317f86b8"
BOT_TOKEN = "8303642695:AAGs0HhQo2fGNTRRVIX4APFcHq7AbpstmlI"
OWNER_ID = 7383046042

FOOTER_FILE = "footer.json"
LINKS_FILE = "links.json"

# Flask for uptime
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

# Redirect route
@app.route('/r/<short_id>')
def redirect_page(short_id):
    links_data = load_links()
    if short_id not in links_data:
        return "Invalid or expired link!"

    original_link = links_data[short_id]

    # HTML redirect template with countdown first, then ads
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirecting...</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                background: #f9f9f9;
                padding: 20px;
            }}
            .countdown {{
                font-size: 20px;
                margin-top: 20px;
                font-weight: bold;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h2>আপনাকে রিডিরেক্ট করা হচ্ছে...</h2>
        <div class="countdown">৭ সেকেন্ড অপেক্ষা করুন...</div>
        
        <!-- Banner Ad -->
        <div style="margin: 20px auto;">
            <script type="text/javascript">
                atOptions = {{
                    'key' : 'dc45da3c7ca351e73e54ca4c2ee9ffdf',
                    'format' : 'iframe',
                    'height' : 250,
                    'width' : 300,
                    'params' : {{}}
                }};
            </script>
            <script type="text/javascript" src="//plugfundsbadger.com/dc45da3c7ca351e73e54ca4c2ee9ffdf/invoke.js"></script>
        </div>

        <!-- Popunder Ad -->
        <script type='text/javascript' src='//plugfundsbadger.com/06/cd/7c/06cd7c54a832b228d22994f008caee85.js'></script>

        <!-- Social Bar Ad -->
        <script type='text/javascript' src='//plugfundsbadger.com/12/7b/62/127b62ade10eea542e84b04aa148b6b3.js'></script>

        <!-- Native Banner Ad -->
        <script async="async" data-cfasync="false" src="//plugfundsbadger.com/4a9890433ba4ffecea5d8eb6290295e6/invoke.js"></script>
        <div id="container-4a9890433ba4ffecea5d8eb6290295e6"></div>

        <script>
            let count = 7;
            const countdownEl = document.querySelector('.countdown');
            const timer = setInterval(() => {{
                count--;
                countdownEl.innerHTML = count + " সেকেন্ড অপেক্ষা করুন...";
                if(count <= 0){{
                    clearInterval(timer);
                    window.location.href = "{original_link}";
                }}
            }}, 1000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

# Functions to manage footer
def load_footer():
    if not os.path.exists(FOOTER_FILE):
        return ""
    with open(FOOTER_FILE, "r") as f:
        return json.load(f).get("footer", "")

def save_footer(text):
    with open(FOOTER_FILE, "w") as f:
        json.dump({"footer": text}, f)

# Functions to manage links
def load_links():
    if not os.path.exists(LINKS_FILE):
        return {}
    with open(LINKS_FILE, "r") as f:
        return json.load(f)

def save_links(data):
    with open(LINKS_FILE, "w") as f:
        json.dump(data, f)

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def short_link(original_link):
    links_data = load_links()
    short_id = generate_short_id()
    links_data[short_id] = original_link
    save_links(links_data)
    # Fixed domain for short link
    return f"https://teraboxlink.free.nf/r/{short_id}"

# Extract all links
def extract_links(text):
    return re.findall(r'https?://\S+', text)

# Start Flask in thread
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
Thread(target=run_flask).start()

# Telegram bot client
bot = Client("media_caption_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Commands
@bot.on_message(filters.private & filters.command("setfooter") & filters.user(OWNER_ID))
async def set_footer_cmd(_, message: Message):
    if len(message.text.split(" ", 1)) < 2:
        return await message.reply("⚠️ ব্যবহার: /setfooter <footer text>")
    footer_text = message.text.split(" ", 1)[1]
    save_footer(footer_text)
    await message.reply("✅ নতুন ফুটার সংরক্ষণ করা হয়েছে।")

@bot.on_message(filters.private & filters.command("removefooter") & filters.user(OWNER_ID))
async def remove_footer_cmd(_, message: Message):
    save_footer("")
    await message.reply("❌ ফুটার মুছে ফেলা হয়েছে।")

@bot.on_message(filters.private & filters.command("viewfooter") & filters.user(OWNER_ID))
async def view_footer_cmd(_, message: Message):
    footer = load_footer()
    if footer:
        await message.reply(f"📌 বর্তমান ফুটার:\n\n{footer}")
    else:
        await message.reply("ℹ️ কোনো ফুটার সেট করা নেই।")

# Media handler
@bot.on_message(filters.private & filters.user(OWNER_ID) & (filters.photo | filters.video))
async def media_handler(client, message: Message):
    if not message.caption:
        return await message.reply("❌ লিংক সহ ক্যাপশন দিন!")

    links = extract_links(message.caption)
    if not links:
        return await message.reply("❌ কোনো লিংক পাওয়া যায়নি ক্যাপশনে!")

    # Shorten all links
    short_links = [short_link(link) for link in links]

    formatted_links = "\n".join([f"Video {i+1}. 👉 {slink}" for i, slink in enumerate(short_links)])
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
