import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread
import yt_dlp

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# --- WEB SERVER (GIỮ MẠNG SỐNG CHO BOT) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "👑 TRỢ LÝ AI ĐẠI ĐẾ ĐANG HOẠT ĐỘNG 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- CHỨC NĂNG XỬ LÝ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # 1. Nếu là Link -> Tải Video
    if "http" in text and ("://" in text):
        msg = await update.message.reply_text("⚡ **Đại Đế đang hút video...**", parse_mode='Markdown')
        
        filename = f"video_{update.message.message_id}.mp4"
        ydl_opts = {
            'outtmpl': filename,
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'noplaylist': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])
                
            await msg.edit_text("🚀 **Đang dâng hàng lên cho chủ nhân...**", parse_mode='Markdown')
            with open(filename, 'rb') as f:
                await update.message.reply_video(video=f, caption="💎 **Hàng về! Phục vụ Đại Đế!**")
            
            os.remove(filename)
            await msg.delete()
        except Exception as e:
            await msg.edit_text(f"❌ Lỗi: {str(e)}")
            
    # 2. Nếu là tin nhắn thường -> Chào hỏi
    else:
        if any(x in text.lower() for x in ['hi', 'chào', 'start', 'alo']):
            await update.message.reply_text("👑 **TRỢ LÝ AI ĐẠI ĐẾ** xin chào chủ nhân!\nGửi link video (TikTok/FB/YouTube) vào đây để em tải ngay!", parse_mode='Markdown')
        else:
            await update.message.reply_text("Gửi Link Video vào đây đi đại ca! Em chỉ nhận Link thôi.")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> AI ĐẠI ĐẾ STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app_bot.run_polling()
