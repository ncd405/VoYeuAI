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
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 TRỢ LÝ AI ĐẠI ĐẾ ĐANG HOẠT ĐỘNG 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- CHỨC NĂNG TẢI VIDEO ---
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Logic trả lời chào hỏi (Nhân cách Đại Đế)
    if not "http" in text:
        if "chào" in text.lower() or "hi" in text.lower() or "start" in text.lower():
            await update.message.reply_text("👑 **TRỢ LÝ AI ĐẠI ĐẾ** xin chào chủ nhân!\nGửi link video vào đây để em xử lý ngay!", parse_mode='Markdown')
        else:
            await update.message.reply_text("Gửi link video TikTok/FB/Youtube vào đây đại ca ơi!")
        return

    msg = await update.message.reply_text("⚡ **Đại Đế đang hút video... (Adrenaline Mode)**", parse_mode='Markdown')
    
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
            
        await msg.edit_text("🚀 **Đang dâng hàng lên cho chủ nhân...**", parse_mode='Markdown')
        with open(filename, 'rb') as f:
            await update.message.reply_video(video=f, caption="💎 **Hàng về! Phục vụ Đại Đế!**")
        
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Lỗi: {str(e)}")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> AI ĐẠI ĐẾ STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
        app_bot.run_polling()
