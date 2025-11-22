import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# --- WEB SERVER GIỮ SỐNG ---
app = Flask(__name__)
@app.route('/')
def home(): return "💎 V17 API MODE IS RUNNING!"
def run_web(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run_web).start()

# --- HÀM GỌI API COBALT (CHÌA KHÓA VẠN NĂNG) ---
def get_media_url(url):
    api_url = "https://api.cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    data = {
        "url": url,
        "vCodec": "h264",
        "vQuality": "max",
        "aFormat": "mp3",
        "filenamePattern": "basic"
    }
    try:
        response = requests.post(api_url, json=data, headers=headers)
        response_json = response.json()
        
        # Kiểm tra kết quả
        if 'url' in response_json:
            return response_json['url']
        elif 'picker' in response_json: # Trường hợp có nhiều video/ảnh
            return response_json['picker'][0]['url']
        else:
            print(f"Lỗi API: {response_json}")
            return None
    except Exception as e:
        print(f"Lỗi kết nối API: {e}")
        return None

# --- XỬ LÝ TIN NHẮN ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if "http" in text:
        msg = await update.message.reply_text("⚡ **Đang nhờ Server xịn tải giúp...**", parse_mode='Markdown')
        
        # 1. Lấy link tải trực tiếp từ API
        direct_url = get_media_url(text)
        
        if direct_url:
            try:
                await msg.edit_text("🚀 **Hàng đã về! Đang gửi...**", parse_mode='Markdown')
                
                # 2. Gửi Video (Telegram tự tải từ URL kia về)
                await update.message.reply_video(
                    video=direct_url, 
                    caption="💎 **Tải thành công! (No Watermark)**"
                )
                await msg.delete()
            except Exception as e:
                # Nếu gửi video lỗi (do file quá to), gửi link tải
                await msg.edit_text(f"⚠️ File quá nặng (>50MB) hoặc Telegram chặn URL.\n👇 **Bấm vào đây để tải:**\n{direct_url}")
        else:
            await msg.edit_text("❌ Link này khó quá, API chưa hỗ trợ hoặc đang bảo trì!")
    else:
        await update.message.reply_text("Gửi Link (TikTok/Youtube/FB) vào đây!")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> V17 API BOT STARTED...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app_bot.run_polling()
