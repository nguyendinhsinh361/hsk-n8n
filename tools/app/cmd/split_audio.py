# Future imports (nếu có)
from __future__ import print_function

# Standard library imports
import os
import re
import io
import pickle
from datetime import datetime
from typing import List, Union, Tuple

# Third-party library imports
from pydub import AudioSegment
import numpy as np
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class AudioSplitter:
    def __init__(self, audio_path: str):
        """
        Initialize audio splitter with source audio file
        
        :param audio_path: Path to the source audio file
        """
        self.source_audio = AudioSegment.from_file(audio_path)
        self.original_filename = os.path.basename(audio_path).split('.')[0]
        
        # Tổng thời lượng audio (milliseconds)
        self.total_duration = len(self.source_audio)

    @staticmethod
    def convert_to_milliseconds(
        time_input: Union[int, float, str, Tuple[int, int, int]]
    ) -> int:
        """
        Chuyển đổi đầu vào thành milliseconds
        
        Hỗ trợ các định dạng:
        - Số nguyên/thực (giây)
        - Chuỗi "HH:MM:SS" 
        - Tuple (giờ, phút, giây)
        
        :param time_input: Đầu vào thời gian
        :return: Thời gian tính bằng milliseconds
        """
        # Nếu là số nguyên hoặc số thực
        if isinstance(time_input, (int, float)):
            return int(time_input * 1000)
        
        # Nếu là chuỗi định dạng "HH:MM:SS"
        if isinstance(time_input, str):
            # Tách các phần của chuỗi
            parts = time_input.split(':')
            
            # Xử lý các trường hợp
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
            elif len(parts) == 2:
                hours = 0
                minutes, seconds = map(int, parts)
            elif len(parts) == 1:
                hours = 0
                minutes = 0
                seconds = int(parts[0])
            else:
                raise ValueError("Định dạng thời gian không hợp lệ")
            
            return int((hours * 3600 + minutes * 60 + seconds) * 1000)
        
        # Nếu là tuple (giờ, phút, giây)
        if isinstance(time_input, tuple):
            if len(time_input) == 3:
                hours, minutes, seconds = time_input
            elif len(time_input) == 2:
                hours = 0
                minutes, seconds = time_input
            elif len(time_input) == 1:
                hours = 0
                minutes = 0
                seconds = time_input[0]
            else:
                raise ValueError("Định dạng tuple không hợp lệ")
            
            return int((hours * 3600 + minutes * 60 + seconds) * 1000)
        
        raise ValueError("Định dạng thời gian không được hỗ trợ")

    def split_by_timestamps(
        self, 
        timestamps: List[Union[Tuple[Union[int, float, str], Union[int, float, str]], List[Union[int, float, str]]]]
    ) -> List[AudioSegment]:
        """
        Cắt audio theo các mốc thời gian
        
        :param timestamps: Danh sách các mốc thời gian
        :return: Danh sách các đoạn audio
        """
        audio_segments = []
        
        for timestamp in timestamps:
            # Hỗ trợ cả tuple và list
            if isinstance(timestamp, tuple):
                start, end = timestamp
            elif isinstance(timestamp, list):
                start, end = timestamp
            else:
                raise ValueError("Định dạng timestamp không hợp lệ")
            
            # Chuyển đổi thời gian
            start_ms = self.convert_to_milliseconds(start)
            end_ms = self.convert_to_milliseconds(end)
            
            # Kiểm tra giới hạn
            start_ms = max(0, start_ms)
            end_ms = min(end_ms, self.total_duration)
            
            # Cắt audio
            segment = self.source_audio[start_ms:end_ms]
            audio_segments.append(segment)
        
        return audio_segments

    def save_audio_segments(
        self, 
        audio_segments: List[AudioSegment], 
        output_directory: str = None, 
        file_format: str = 'mp3', 
        filename: str = 'audio_segment'
    ) -> List[str]:
        """
        Lưu các đoạn audio
        
        :param audio_segments: Danh sách các đoạn audio
        :param output_directory: Thư mục xuất
        :param file_format: Định dạng file
        :param filename: Tên file
        :return: Danh sách đường dẫn file đã lưu
        """
        # Tạo thư mục nếu chưa tồn tại
        if output_directory is None:
            output_directory = os.path.join(
                os.getcwd(), 
                "app/data/input"
            )
        os.makedirs(output_directory, exist_ok=True)
        
        # Lưu các đoạn audio
        saved_files = []
        for index, segment in enumerate(audio_segments, 1):
            output_path = os.path.join(output_directory, f"{filename}.{file_format}")
            
            segment.export(output_path, format=file_format)
            saved_files.append(output_path)
            print(f"Exported: {output_path}")
        
        return saved_files

# Tích hợp vào AudioSplitter
class EnhancedAudioSplitter(AudioSplitter):
    def __init__(
        self, 
        audio_path
    ):
        super().__init__(audio_path)

    def split_audio(
        self, 
        timestamps, 
        file_format='mp3', 
        filename='audio_segment_',
        output_directory=None
    ):
        """
        Cắt và lưu các đoạn audio
        
        :param timestamps: Danh sách mốc thời gian
        :param file_format: Định dạng file
        :param filename_prefix: Tiền tố tên file
        :param output_directory: Thư mục lưu các file đã cắt
        :return: Danh sách file đã lưu
        """
        # Cắt audio
        segments = self.split_by_timestamps(timestamps)
        
        # Lưu file
        if output_directory is None:
            output_directory = "app/data/split"
            
        saved_files = self.save_audio_segments(
            segments, 
            file_format=file_format,
            output_directory=output_directory,
            filename=filename
        )
        
        return saved_files

def extract_file_id_from_drive_link(drive_link):
    """
    Trích xuất ID file từ Google Drive link
    _timp
    :param drive_link: Link Google Drive
    :return: ID của file
    """
    # Mẫu regex để tìm ID file từ link Google Drive
    pattern = r"/d/([a-zA-Z0-9_-]+)"
    match = re.search(pattern, drive_link)
    
    if match:
        return match.group(1)
    
    # Thử mẫu khác nếu không khớp
    pattern = r"id=([a-zA-Z0-9_-]+)"
    match = re.search(pattern, drive_link)
    
    if match:
        return match.group(1)
    
    raise ValueError("Không thể trích xuất ID file từ link Google Drive")

def download_from_drive(drive_link, output_path, socket_timeout=300, max_attempts=3, max_chunk_attempts=3):
    """
    Tải file từ Google Drive sử dụng OAuth credentials
    
    :param drive_link: Link Google Drive
    :param output_path: Đường dẫn để lưu file
    :param socket_timeout: Thời gian timeout cho socket (giây)
    :param max_attempts: Số lần thử tải lại toàn bộ file
    :param max_chunk_attempts: Số lần thử tải lại một chunk
    :return: Đường dẫn đến file đã tải
    """
    # Import cần thiết
    import socket
    import time
    from datetime import datetime
    
    def log_message(message):
        """Ghi log với timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    # Trích xuất ID file từ link
    file_id = extract_file_id_from_drive_link(drive_link)
    log_message(f"Bắt đầu tải file với ID: {file_id}")
    
    # Thiết lập phạm vi quyền truy cập
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    creds = None
    # Token đã lưu trước đó
    token_path = 'app/auth/token_downloads_audio.json'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Nếu không có credentials hợp lệ, thì yêu cầu người dùng đăng nhập
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            log_message("Đã làm mới token hết hạn")
        else:
            # Sử dụng credentials.json để xác thực
            log_message("Bắt đầu quá trình xác thực mới")
            flow = InstalledAppFlow.from_client_secrets_file(
                'app/auth/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            log_message("Xác thực hoàn tất")
        
        # Lưu credentials để sử dụng lần sau
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            log_message("Đã lưu token mới")
    
    # Xây dựng service
    service = build('drive', 'v3', credentials=creds)
    
    # Tạo thư mục chứa file nếu chưa tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    log_message(f"Đã tạo thư mục đích: {os.path.dirname(output_path)}")
    
    # Thiết lập timeout mặc định cho socket
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(socket_timeout)
    log_message(f"Đã thiết lập socket timeout: {socket_timeout} giây")
    
    try:
        # Tải file
        request = service.files().get_media(fileId=file_id)
        file_output_path = f"{output_path}{file_id}.mp3"
        log_message(f"Đường dẫn file đích: {file_output_path}")
        
        # Thêm xử lý timeout và retry
        download_attempts = 0
        
        while download_attempts < max_attempts:
            try:
                with open(file_output_path, 'wb') as f:
                    downloader = MediaIoBaseDownload(f, request)
                    done = False
                    chunk_attempts = 0
                    
                    while not done:
                        try:
                            status, done = downloader.next_chunk()
                            log_message(f"Đã tải {int(status.progress() * 100)}%")
                            chunk_attempts = 0  # Reset counter on successful chunk
                        except (TimeoutError, socket.timeout, socket.error) as timeout_err:
                            # Xử lý lỗi timeout cụ thể
                            chunk_attempts += 1
                            log_message(f"Timeout khi tải chunk (lần {chunk_attempts}/{max_chunk_attempts}): {str(timeout_err)}")
                            
                            if chunk_attempts >= max_chunk_attempts:
                                log_message("Đã vượt quá số lần thử lại cho chunk hiện tại, sẽ thử lại toàn bộ quá trình tải.")
                                raise  # Re-raise để chuyển sang retry toàn bộ file
                            
                            # Chờ trước khi thử lại chunk
                            wait_time = 2 ** chunk_attempts
                            log_message(f"Chờ {wait_time} giây trước khi thử lại chunk...")
                            time.sleep(wait_time)
                            continue
                
                # Nếu tải thành công, thoát vòng lặp retry
                log_message(f"Đã tải file thành công: {file_output_path}")
                return file_output_path
            
            except Exception as e:
                download_attempts += 1
                log_message(f"Lỗi khi tải file (lần {download_attempts}/{max_attempts}): {str(e)}")
                
                # Nếu còn lần thử, chờ một chút trước khi thử lại
                if download_attempts < max_attempts:
                    wait_time = 2 ** download_attempts  # Backoff strategy
                    log_message(f"Chờ {wait_time} giây trước khi thử lại...")
                    time.sleep(wait_time)
                else:
                    log_message(f"Đã thử {max_attempts} lần, không thể tải file.")
                    raise
        
        # Nếu tất cả các lần thử đều thất bại
        raise Exception(f"Không thể tải file sau {max_attempts} lần thử")
        
    finally:
        # Khôi phục giá trị timeout ban đầu
        socket.setdefaulttimeout(original_timeout)
        log_message("Đã khôi phục cấu hình socket ban đầu")

def download_from_drive_with_service_account(drive_link, output_path):
    """
    Tải file từ Google Drive sử dụng Service Account credentials
    
    :param drive_link: Link Google Drive
    :param output_path: Đường dẫn để lưu file
    :return: Đường dẫn đến file đã tải
    """
    # Trích xuất ID file từ link
    file_id = extract_file_id_from_drive_link(drive_link)
    
    # Phạm vi quyền truy cập
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    # Tạo credentials từ file credentials.json
    credentials = service_account.Credentials.from_service_account_file(
        'app/auth/credentials.json', scopes=SCOPES)
    
    # Xây dựng service
    service = build('drive', 'v3', credentials=credentials)
    
    # Tạo thư mục chứa file nếu chưa tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Tải file
    request = service.files().get_media(fileId=file_id)
    
    with open(output_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Đã tải {int(status.progress() * 100)}%")
    
    print(f"Đã tải file thành công: {output_path}")
    return output_path