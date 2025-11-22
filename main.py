import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread
import yt_dlp
import requests

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "👑 TRỢ LÝ AI ĐẠI ĐẾ (ANTI-BLOCK MODE) ONLINE!"
def run_web(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run_web).start()

# --- HÀM GIẢI MÃ LINK RÚT GỌN (QUAN TRỌNG CHO DOUYIN) ---
def get_real_url(short_url):
    try:
        # Giả danh iPhone để lấy link gốc
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
        response = requests.head(short_url, allow_redirects=True, headers=headers)
        return response.url
    except:
        return short_url

# --- CHỨC NĂNG TẢI VIDEO ---
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Logic tải video
    if "http" in text:
        msg = await update.message.reply_text("⚡ **Đại Đế đang phá tường lửa để hút video...**", parse_mode='Markdown')
        
        # 1. Lấy link thật (nếu là link rút gọn v.douyin...)
        real_url = get_real_url(text)
        print(f"Link gốc: {real_url}")

        filename = f"video_{update.message.message_id}.mp4"
        
        # 2. Cấu hình yt-dlp "Tàng Hình" (Giả danh iPhone)
        ydl_opts = {
            'outtmpl': filename,
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True, # Bỏ qua lỗi SSL
            'ignoreerrors': True,
            # Dòng này quan trọng nhất: Giả làm iPhone
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'http_headers': {
                'Referer': 'https://www.tiktok.com/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([real_url])
            
            if os.path.exists(filename):
                await msg.edit_text("🚀 **Đang dâng hàng lên...**", parse_mode='Markdown')
                with open(filename, 'rb') as f:
                    await update.message.reply_video(video=f, caption="💎 **Video sạch (No Watermark)!**")
                os.remove(filename)
                await msg.delete()
            else:
                await msg.edit_text("❌ TikTok chặn căng quá! Thử link khác xem sao.")
                
        except Exception as e:
            await msg.edit_text(f"❌ Lỗi: {str(e)}")
            
    else:
        await update.message.reply_text("Gửi Link Video vào đây đi đại ca!")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> AI ĐẠI ĐẾ (ANTI-BLOCK) STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))
        app_bot.run_polling()
