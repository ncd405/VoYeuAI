import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread
import yt_dlp

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# --- WEB SERVER (TRÁI TIM BẤT TỬ) ---
# Đây là phần quan trọng nhất để đánh lừa Render rằng "Web này đang có người truy cập"
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 BOT IS ALIVE! PING ME TO KEEP ALIVE!"

def run_web():
    # Render sẽ cấp cổng qua biến môi trường PORT, mặc định là 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- CHỨC NĂNG TẢI VIDEO ---
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "http" not in text:
        await update.message.reply_text("Gửi link video vào đây đại ca ơi!")
        return

    msg = await update.message.reply_text("⚡ Đang hút video... (Adrenaline Mode)")
    
    filename = f"video_{update.message.message_id}.mp4"
    ydl_opts = {
        'outtmpl': filename,
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'noplaylist': True
    }
    
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([text])
            
        await msg.edit_text("🚀 Đang bắn qua Telegram...")
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption="💎 Hàng về! Bot Bất Tử!")
        
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Lỗi: {str(e)}")

if __name__ == '__main__':
    # Kích hoạt tim nhân tạo trước
    keep_alive()
    
    # Kích hoạt Bot
    if TELEGRAM_TOKEN:
        print(">>> BOT STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
        app_bot.run_polling()
