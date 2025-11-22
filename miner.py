import os
import time
from telethon import TelegramClient
from colorama import Fore, Style, init

init(autoreset=True)

# Lấy thông tin từ Biến Môi Trường (RENDER ENV)
# RENDER SẼ TỰ ĐỘNG CUNG CẤP CÁC THÔNG TIN NÀY
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
PHONE = os.environ.get('PHONE_NUMBER')
BOT_USERNAME = "@BlumCryptoBot" # Thay bằng Bot Coin bạn muốn đào

client = TelegramClient('session_render', API_ID, API_HASH)

async def main():
    print(f"{Fore.YELLOW}🚀 ĐANG KẾT NỐI VÀ ĐĂNG NHẬP TRÊN SERVER AiDaide...{Style.RESET_ALL}")
    
    # Kết nối
    await client.start(phone=PHONE)
    print(f"{Fore.GREEN}✅ ĐĂNG NHẬP THÀNH CÔNG! Bắt đầu chu trình đào coin 24/7.{Style.RESET_ALL}")
    
    # --- VÒNG LẶP ĐÀO COIN VĨNH CỬU ---
    while True:
        try:
            print(f"\n{Fore.CYAN}--- LỆNH ĐÀO MỚI ---{Style.RESET_ALL}")
            
            # Gửi lệnh /start (Bot Coin sẽ hiểu là Claim/Start)
            await client.send_message(BOT_USERNAME, '/start') 
            print(f"{Fore.GREEN}✅ Đã gửi lệnh /start tới {BOT_USERNAME}")
            
            # Đợi 1 tiếng (3600 giây) rồi đào tiếp
            print(f"{Fore.BLUE}💤 Đang ngủ... Chờ 60 phút để Claim lượt tiếp theo...{Style.RESET_ALL}")
            time.sleep(3600) 
            
        except Exception as e:
            print(f"{Fore.RED}❌ Lỗi xảy ra: {e}. Thử lại sau 5 phút.")
            time.sleep(300)

with client:
    client.loop.run_until_complete(main())
