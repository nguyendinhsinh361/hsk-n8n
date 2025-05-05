import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logging():
    """Thiết lập cấu hình logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

def get_current_time() -> str:
    """Trả về thời gian hiện tại dưới dạng chuỗi"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_data(data: dict, required_fields: list) -> bool:
    """Kiểm tra dữ liệu có chứa các trường bắt buộc hay không"""
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True
