from enum import Enum

class Telegram:
    BOT_ID = {
        "migii_hsk_route_pass_refund_bot": "7727369137:AAECvNmDGfZC2UyVXgAHG-S0wsx4SvDICkQ",
    }
    
    CHAT_ID = {
        "MIGII_HSK_ROUTE_PASS_REFUND": "-1002697642986",
    }
    
    COMMAND_ID = {
        "audio_extract": "1N3B_P1wtxQOC0kGx5-AmCjWUs_7rNdS8",
        "image_extract": "17b7AtDk7RdGb1jr1WlV_d3msRU-WKP9b",
        "pdf_exam_extract": "1TmgkeQpbx3GqItz5DGYBA7kNvVf4W7cs",
    }

class BotTelegramEnum(str, Enum):
    MIGII_HSK_ROUTE_PASS_REFUND_BOT = "migii_hsk_route_pass_refund_bot"

class CommandTelegramEnum(str, Enum):
    DOWLOADS_FILES = "abc"
    
class ChatIDTelegramEnum(str, Enum):
    MIGII_HSK_ROUTE_PASS_REFUND = "MIGII_HSK_ROUTE_PASS_REFUND"