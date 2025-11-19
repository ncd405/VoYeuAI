import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os

# --- CẤU HÌNH (Tự động lấy từ Server nếu có, hoặc nhập tay) ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "NHAP_TOKEN_CUA_BAN_VAO_DAY_NEU_CHAY_TAY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "NHAP_API_KEY_CUA_BAN_VAO_DAY_NEU_CHAY_TAY")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

async def chat_voi_vo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text: return
    print(f"📩 Nhận: {user_text}")
    try:
        response = model.generate_content(user_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Lỗi: {e}")

if __name__ == '__main__':
    print(">>> BOT ĐANG CHẠY...")
    app = ApplicationBuilder().

