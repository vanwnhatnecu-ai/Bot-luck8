import os
import requests
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import logging
from datetime import datetime
import time

# Thiết lập logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Thông tin bot
BOT_TOKEN = os.environ.get('8318094060:AAGXPli-P7R2Fu4GvGwEi3NrpXaR9AlgbFM')
API_URL = "https://b52-chaoconnha-bobinn.onrender.com/api/taixiumd5"
ADMIN_INFO = {
    "name": "Admin LuckWin",
    "contact": "@luckwin_admin",
    "website": "https://luckwin.com"
}

# Biến toàn cục
active_chats = set()  # Lưu trữ các chat đang active
last_data = None
last_update_time = 0

class LotteryBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Thiết lập các command handler"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("chaybot", self.activate_bot))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh /start"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        welcome_text = f"""
<b>👋 Chào mừng {user.first_name} đến với LUCKWIN MD5!</b>

🤖 <b>Đây là bot phân tích xúc xắc chính xác cao</b>
💎 <b>Sử dụng AI để dự đoán kết quả xúc xắc</b>

<b>📋 Các lệnh có sẵn:</b>
/start - Hiển thị thông tin này
/chaybot - Kích hoạt bot phân tích

<b>👤 Thông tin Admin:</b>
• Tên: {ADMIN_INFO['name']}
• Liên hệ: {ADMIN_INFO['contact']}
• Website: {ADMIN_INFO['website']}

<b>✨ Chúc bạn may mắn!</b>
        """
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)
        
    async def activate_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xử lý lệnh /chaybot"""
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        if chat_id in active_chats:
            await update.message.reply_text("🤖 <b>Bot đã được kích hoạt trước đó!</b>", parse_mode=ParseMode.HTML)
            return
            
        active_chats.add(chat_id)
        
        if chat_type == "private":
            await update.message.reply_text(
                "🚀 <b>Bot đã được kích hoạt!</b>\n\n"
                "🤖 <b>Bắt đầu phân tích dữ liệu tự động...</b>\n"
                "📊 <b>Bot sẽ gửi thông báo ngay khi có dữ liệu mới</b>", 
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                "🚀 <b>Bot đã được kích hoạt trong nhóm!</b>\n\n"
                "🤖 <b>Bắt đầu phân tích dữ liệu tự động...</b>\n"
                "📊 <b>Bot sẽ gửi thông báo ngay khi có dữ liệu mới</b>\n"
                "👥 <b>Tất cả thành viên đều có thể xem phân tích</b>", 
                parse_mode=ParseMode.HTML
            )
        
        logger.info(f"Bot activated in chat: {chat_id} (type: {chat_type})")
        
    async def fetch_data(self):
        """Lấy dữ liệu từ API"""
        try:
            response = requests.get(API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Data fetched successfully: {data}")
                return data
            else:
                logger.error(f"API returned error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def format_message(self, data):
        """Định dạng tin nhắn từ dữ liệu API với chữ đậm"""
        try:
            # Extract data from API response
            phien = data.get('Phien', 'N/A')
            d1 = data.get('Xuc_xac_1', 'N/A')
            d2 = data.get('Xuc_xac_2', 'N/A')
            d3 = data.get('Xuc_xac_3', 'N/A')
            tong = data.get('Tong', 'N/A')
            ket_qua = data.get('Ket_qua', 'N/A')

# Prediction data
            phien_tiep_theo = data.get('Phien_tiep_theo', 'N/A')
            du_doan = data.get('Du_doan', 'N/A')
            do_tin_cay = data.get('Do_tin_cay', 'N/A')

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format message with bold text using HTML
            message = f"""
<b>♦️ LUCKWIN MD5 - PHÂN TÍCH CHUẨN XÁC ♦️</b>
══════════════════════════
<b>🆔 Phiên:</b> {phien}
<b>🎲 Xúc xắc:</b> {d1} + {d2} + {d3}
<b>🧮 Tổng điểm:</b> {tong} | <b>Kết quả:</b> 💰 {ket_qua}
──────────────────────────
<b>🔮 Dự đoán phiên {phien_tiep_theo}:</b> 🀄️ {du_doan}
<b>📊 Độ tin cậy:</b> ↪️ ({do_tin_cay}%)
<b>🎯 Khuyến nghị:</b> Đặt cược {du_doan}

<b>⏱️ Thời gian:</b> {current_time}
══════════════════════════
<b>👥 Hệ thống phân tích nâng cao 👥</b>
<b>💎 Uy tín - Chính xác - Hiệu quả 💎</b>
            """
            return message
        except Exception as e:
            logger.error(f"Error formatting message: {e}")
            # Fallback message if data structure is different
            return f"""
<b>♦️ LUCKWIN MD5 - PHÂN TÍCH CHUẨN XÁC ♦️</b>
══════════════════════════
<b>🆔 Phiên:</b> {data.get('round_id', 'N/A')}
<b>🎲 Xúc xắc:</b> {data.get('dice', 'N/A')}
<b>🧮 Tổng điểm:</b> {data.get('total', 'N/A')} | <b>Kết quả:</b> 💰 {data.get('result', 'N/A')}
──────────────────────────
<b>🔮 Dự đoán phiên {data.get('next_round', 'N/A')}:</b> 🀄️ {data.get('prediction', 'N/A')}
<b>📊 Độ tin cậy:</b> ↪️ ({data.get('confidence', 'N/A')}%)
<b>🎯 Khuyến nghị:</b> Đặt cược {data.get('prediction', 'N/A')}

<b>⏱️ Thời gian:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
══════════════════════════
<b>👥 Hệ thống phân tích nâng cao 👥</b>
<b>💎 Uy tín - Chính xác - Hiệu quả 💎</b>
            """
    
    async def send_update_to_chat(self, chat_id, data):
        """Gửi tin nhắn cập nhật tới một chat cụ thể"""
        try:
            message = self.format_message(data)
            if message:
                await self.application.bot.send_message(
                    chat_id=chat_id, 
                    text=message, 
                    parse_mode=ParseMode.HTML
                )
                logger.info(f"Sent update to chat: {chat_id}")
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            # Remove chat from active list if there's an error (e.g., bot was removed from group)
            if chat_id in active_chats:
                active_chats.remove(chat_id)
                logger.info(f"Removed chat {chat_id} from active list due to error")
    
    async def check_and_broadcast_updates(self):
        """Kiểm tra và gửi cập nhật tới tất cả active chats"""
        global last_data, last_update_time
        
        try:
            new_data = await self.fetch_data()
            
            if new_data and new_data != last_data:
                logger.info("New data detected, broadcasting to all active chats")
                last_data = new_data
                last_update_time = time.time()
                
                # Gửi tới tất cả active chats
                tasks = []
                for chat_id in list(active_chats):
                    tasks.append(self.send_update_to_chat(chat_id, new_data))
                
                # Chạy đồng thời
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
            else:
                logger.info("No new data detected")
                
        except Exception as e:
            logger.error(f"Error in update check: {e}")
    
    async def monitoring_loop(self):
        """Vòng lặp giám sát chính"""
        logger.info("Starting monitoring loop...")
        
        while True:
            try:
                if active_chats:  # Chỉ kiểm tra nếu có chat active
                    await self.check_and_broadcast_updates()
                else:
                    logger.info("No active chats, skipping check")
                
                # Kiểm tra mỗi 10 giây để đảm bảo cập nhật nhanh
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)
    
    def run(self):
        """Chạy bot"""
        logger.info("Starting bot...")
        
        # Khởi chạy vòng lặp giám sát
        asyncio.create_task(self.monitoring_loop())
        
        # Chạy bot
        self.application.run_polling()

def main():
    """Hàm chính"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        print("❌ Vui lòng thiết lập BOT_TOKEN trong Environment Variables!")
        return
    
    try:
        bot = LotteryBot(BOT_TOKEN)
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()
