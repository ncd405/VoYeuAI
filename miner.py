import os
import time
from telethon import TelegramClient
from telethon.tl.functions.messages import GetBotCommandsRequest
from telethon.errors import SessionPasswordNeededError
from colorama import Fore, Style, init

init(autoreset=True)

# 1. Lấy thông tin từ Biến Môi Trường (RENDER ENV)
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
PHONE = os.environ.get('PHONE_NUMBER')

# 2. Định nghĩa Bot mục tiêu (Thay bằng Bot Coin của bạn)
BOT_USERNAME = "@BlumCryptoBot" # Vd: Blum, Major, v.v.

# 3. Kết nối Client
client = TelegramClient('session_render', API_ID, API_HASH)

async def main():
    print(f"{Fore.YELLOW}🚀 BẮT ĐẦU ĐĂNG NHẬP TRÊN SERVER RENDER...")
    
    # Kiểm tra và kết nối
    await client.start(phone=PHONE)
    print(f"{Fore.GREEN}✅ ĐĂNG NHẬP THÀNH CÔNG!")
    
    # --- VÒNG LẶP ĐÀO COIN VĨNH CỬU ---
    while True:
        try:
            print(f"{Fore.CYAN}--- LỆNH MỚI ---")
            
            # Gửi lệnh /start (Tùy thuộc vào Bot)
            await client.send_message(BOT_USERNAME, '/start')
            print(f"{Fore.GREEN}✅ Đã gửi lệnh /start tới {BOT_USERNAME}")
            
            # Chờ 3 giây để Bot phản hồi
            time.sleep(3)
            
            # (Thường là lệnh /claim hoặc /tap)
            # Tùy chỉnh ở đây nếu Bot của bạn dùng lệnh khác
            # await client.send_message(BOT_USERNAME, '/claim') 

            print(f"{Fore.BLUE}💤 Đang ngủ... 60 phút sau sẽ đào tiếp.")
            # Đào coin không nên làm quá nhanh
            time.sleep(3600) # Đợi 1 tiếng (3600 giây)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi xảy ra: {e}. Thử lại sau 5 phút.")
            time.sleep(300)

with client:
    client.loop.run_until_complete(main())
