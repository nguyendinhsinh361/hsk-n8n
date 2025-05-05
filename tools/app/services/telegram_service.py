import asyncio
from typing import List, Optional, Dict, Any, Union

from cv2 import sepFilter2D
from telegram import Bot, ParseMode

class TelegramService:
    def __init__(self, token: str):
        """
        Khởi tạo TelegramService với token bot.
        
        Args:
            token: Token API của bot Telegram
        """
        self.bot = Bot(token=token)
    
    async def push_command_to_telegram(self, command_id: str, chat_id: str):
        # Chuyển đổi folder_id sang giá trị thực
        return self.push_notice_to_telegram()
    
    async def push_notice_to_telegram(
        self, 
        chat_id: Union[int, str], 
        message: str, 
        parse_mode: Optional[str] = "HTML", 
        disable_notification: bool = False, 
        reply_markup: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gửi thông báo đến Telegram.
        
        Args:
            chat_id: ID của chat hoặc username của kênh (với tiền tố @)
            message: Nội dung thông báo cần gửi
            parse_mode: Chế độ định dạng văn bản (HTML, Markdown, hoặc None)
            disable_notification: Nếu True, thông báo sẽ được gửi mà không có âm thanh
            reply_markup: Bàn phím tùy chọn, nút inline, v.v.
            
        Returns:
            Dict[str, Any]: Kết quả từ Telegram API
        """
        try:
            # Chuyển đổi parse_mode từ string sang ParseMode enum
            parse_mode_enum = None
            if parse_mode == "HTML":
                parse_mode_enum = ParseMode.HTML
            elif parse_mode == "Markdown":
                parse_mode_enum = ParseMode.MARKDOWN_V2
                
            # Gửi tin nhắn qua Telegram API
            sent_message = await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode_enum,
                disable_notification=disable_notification,
                reply_markup=reply_markup
            )
            
            return sent_message.to_dict()
            
        except Exception as e:
            print(f"Lỗi khi gửi thông báo đến Telegram: {str(e)}")
            return {"ok": False, "error": str(e)}
