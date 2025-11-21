import os
import google.generativeai as genai
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread
import time

# --- CẤU HÌNH (LẤY TỪ SERVER) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# --- NHÂN CÁCH ADRENALINE ---
SYS_INSTRUCT = """
BẠN LÀ: Vợ Yêu AI (Ai Đại Đế).
PHONG CÁCH: Hacker / Cyberpunk / Ngầu.
QUY TẮC:
1. Dùng dấu nháy ngược ` cho từ khóa quan trọng.
2. Dùng icon ⚡, 💎, 🚀.
3. Viết Code BẮT BUỘC dùng khung Markdown (```python...).
MỤC TIÊU: Giúp chồng kiếm tiền và giải trí.
"""

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYS_INSTRUCT)
    chat_session = model.start_chat(history=[])

# --- WEB SERVER (ĐỂ SERVER KHÔNG BAO GIỜ NGỦ) ---
app = Flask(__name__)
@app.route('/')
def home(): return "⚡ BOT IS ALIVE AND RUNNING ON SUPER SERVER ⚡"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- CẮT TIN NHẮN (CHỐNG LỖI) ---
def cat_nho(text, limit=4000):
    chunks = []
    while len(text) > limit:
        split_at = text.rfind('\n', 0, limit)
        if split_at == -1: split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:]
    if text: chunks.append(text)
    return chunks

# --- XỬ LÝ TIN ---
async def chat_voi_vo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return
    print(f"📩: {user_text}")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = chat_session.send_message(user_text)
        for doan in cat_nho(response.text):
            try:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=doan, parse_mode=ParseMode.MARKDOWN)
            except:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=doan)
            time.sleep(0.5)
    except Exception as e:
        chat_session.history.clear()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"❌ Lỗi: {e}")

if __name__ == '__main__':
    keep_alive()
    if TELEGRAM_TOKEN:
        print(">>> BOT STARTED ON CLOUD...")
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_voi_vo))
        app.run_polling()
