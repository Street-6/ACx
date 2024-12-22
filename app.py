import asyncio
from fastapi import FastAPI, Request 
from fastapi.responses import JSONResponse 
from telebot import TeleBot, types
import httpx
import re
from threading import Thread
import os 
import logging 
import uvicorn 

app = FastAPI()
bot = TeleBot("7608513610:AAEaq5POwJulje5FG5-hG_uzKkL4JSPcw5w")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def get_mpd_link(url):
    try:
        response = httpx.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Failed to retrieve the page: Status code {response.status_code}"
        page_content = response.text
        mpd_pattern = r'(https?://[^\s]+\.mpd)'
        mpd_links = re.findall(mpd_pattern, page_content)
        title_pattern = r'<title>(.*?)</title>'
        title = re.search(title_pattern, page_content)
        title = title.group(1) if title else "Unknown Title"
        if mpd_links:
            return {
                "title": title,
                "mpd_link": mpd_links[0].split(',')[0]
            }
        else:
            return "No .mpd link found on the page."
    except Exception as e:
        return f"Error occurred: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! To Lullichor , use /mpd")

@bot.message_handler(func=lambda message: message.text.startswith('/mpd'))
def scrape_mpd(message):
    """Handles the /mpd command"""
    text = message.text.split()
    if len(text) < 2:
        bot.send_message(message.chat.id, "Abe 😑 Lulli aadmi URL to bhej sath mai")
        return
    
    url = text[1]
    result = get_mpd_link(url)
    
    if isinstance(result, dict):
        bot.send_message(message.chat.id, f"<b>Title: {result['title']}</b>\n\nMPD Link: {result['mpd_link']}\n")
    else:
        bot.send_message(message.chat.id, result)

def start_bot():
    """Start the Telegram bot"""
    logging.info("Starting the bot...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Error occurred while polling: {e}")

# FastAPI route
@app.route("/", methods=["GET", "HEAD"])
async def index(request: Request):
    logging.info("Received request to /")
    return JSONResponse(content={"message": "Service is running"}, media_type="application/json", status_code=200)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    # Run the bot in a separate thread
    Thread(target=start_bot).start()
    
    # Start FastAPI web server
    uvicorn.run(app, host="0.0.0.0", port=port)
