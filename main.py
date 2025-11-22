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
def home(): return "🎥 BOT MOVIE DOWNLOADER V15 ONLINE!"
def run_web(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run_web).start()

# --- HÀM UPLOAD GOFILE (CHO FILE NẶNG) ---
def upload_to_gofile(file_path):
    try:
        # Tìm server tốt nhất
        server = requests.get("https://api.gofile.io/getServer").json()['data']['server']
        # Upload
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"https://{server}.gofile.io/uploadFile",
                files={'file': f}
            ).json()
        if response['status'] == 'ok':
            return response['data']['downloadPage']
    except Exception as e:
        print(f"Lỗi Gofile: {e}")
    return None

# --- CHỨC NĂNG TẢI ---
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if "http" in text:
        msg = await update.message.reply_text("🍿 **Phát hiện Link Phim/Video!**\n⚡ Đang khởi động máy hút...", parse_mode='Markdown')
        
        filename = f"movie_{update.message.message_id}.mp4"
        
        # Cấu hình yt-dlp ĂN TẠP (Chấp hết các loại web)
        ydl_opts = {
            'outtmpl': filename,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Ưu tiên chất lượng cao nhất
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'geo_bypass': True, # Vượt chặn quốc gia
            # Giả danh máy tính Windows để vào web phim
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'http_headers': {'Referer': text} # Đánh lừa server phim
        }
        
        try:
            # 1. Tải về Server Render
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                title = info.get('title', 'Video Phim')
                
            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / (1024 * 1024) # MB
                
                # 2. Phân loại xử lý
                if file_size < 49:
                    await msg.edit_text(f"🚀 **Đang gửi video ({file_size:.1f}MB)...**", parse_mode='Markdown')
                    with open(filename, 'rb') as f:
                        await update.message.reply_video(video=f, caption=f"🎬 **{title}**")
                else:
                    await msg.edit_text(f"⚠️ **Phim nặng ({file_size:.1f}MB)!**\n⚡ Đang chuyển sang Link tải nhanh...", parse_mode='Markdown')
                    
                    # Upload lên Gofile
                    link_tai = upload_to_gofile(filename)
                    
                    if link_tai:
                        await update.message.reply_text(
                            f"🎬 **{title}**\n"
                            f"📦 Dung lượng: {file_size:.2f} MB\n"
                            f"🚀 **BẤM VÀO ĐÂY ĐỂ TẢI (Max Speed):**\n{link_tai}",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text("❌ File quá nặng, không tạo được link tải!")

                os.remove(filename) # Dọn rác
                await msg.delete()
            else:
                await msg.edit_text("❌ Web này chặn Bot rồi! (Hoặc link hỏng)")
                
        except Exception as e:
            await msg.edit_text(f"❌ Lỗi: {str(e)}")
    else:
        await update.message.reply_text("Gửi Link Phim/Video vào đây đại ca!")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> MOVIE BOT STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
        app_bot.run_polling()
