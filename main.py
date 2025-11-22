import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread
import yt_dlp
import requests
import time

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "🚀 V16 ANTI-BOT YOUTUBE IS RUNNING!"
def run_web(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run_web).start()

# --- HÀM UPLOAD GOFILE (CHO FILE NẶNG) ---
def upload_to_gofile(file_path):
    try:
        server = requests.get("https://api.gofile.io/getServer").json()['data']['server']
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"https://{server}.gofile.io/uploadFile",
                files={'file': f}
            ).json()
        if response['status'] == 'ok':
            return response['data']['downloadPage']
    except: return None

# --- CHỨC NĂNG TẢI ---
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if "http" in text:
        msg = await update.message.reply_text("⚡ **Phát hiện Link! Đang giả dạng Android để tải...**", parse_mode='Markdown')
        
        filename = f"video_{update.message.message_id}.mp4"
        
        # CẤU HÌNH VƯỢT TƯỜNG LỬA YOUTUBE
        ydl_opts = {
            'outtmpl': filename,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            # --- BÍ KÍP VƯỢT LỖI SIGN IN ---
            # Ép buộc dùng API của Android/iOS thay vì Web
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                title = info.get('title', 'Video Downloaded')
                
            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / (1024 * 1024)
                
                if file_size < 49:
                    await msg.edit_text("🚀 **Đang bắn hàng...**", parse_mode='Markdown')
                    with open(filename, 'rb') as f:
                        await update.message.reply_video(video=f, caption=f"🎬 **{title}**")
                else:
                    await msg.edit_text(f"⚠️ **Nặng {file_size:.1f}MB!** Đang up lên Cloud...", parse_mode='Markdown')
                    link_tai = upload_to_gofile(filename)
                    if link_tai:
                        await update.message.reply_text(f"🎬 **{title}**\n🚀 **Link tải Max Speed:**\n{link_tai}", parse_mode='Markdown')
                    else:
                        await update.message.reply_text("❌ File nặng quá mà Gofile bị lỗi rồi!")

                os.remove(filename)
                await msg.delete()
            else:
                await msg.edit_text("❌ YouTube chặn căng quá! Thử lại sau ít phút.")
                
        except Exception as e:
            await msg.edit_text(f"❌ Lỗi: {str(e)}")
    else:
        await update.message.reply_text("Gửi Link vào đây đi đại ca!")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> V16 STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
        app_bot.run_polling()
