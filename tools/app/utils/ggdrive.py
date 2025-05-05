# Future imports (nếu có)
from __future__ import print_function

# Standard library imports
import os
import io
import pickle
import logging
import time

# Third-party library imports
from pydub import AudioSegment
from googleapiclient.discovery import build
import os
import numpy as np
from datetime import datetime
from typing import List, Union, Tuple, Optional, Dict
from google.oauth2.credentials import Credentials
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

class FileTypeGroups:
    """Nhóm các loại file phổ biến"""
    
    MICROSOFT_OFFICE = [
        '.doc', '.docx',   # Word
        '.xls', '.xlsx',   # Excel
        '.ppt', '.pptx',   # PowerPoint
        '.mdb',            # Access
    ]
    
    TEXT_FILES = [
        '.txt',            # Plain text
        '.rtf',            # Rich Text Format
        '.csv',            # Comma-Separated Values
        '.log',            # Log files
        '.md'              # Markdown
    ]
    
    DOCUMENTS = [
        '.pdf',            # PDF
        '.xml',            # XML
        '.json',           # JSON
    ]
    
    COMPRESSED = [
        '.zip', '.rar', 
        '.7z', '.gz'
    ]
    
    AUDIO = [
        '.mp3',            # MP3 audio
        '.wav',            # WAV audio
        '.flac',           # FLAC audio
        '.aac',            # AAC audio
        '.wma',            # Windows Media Audio
        '.m4a',            # MPEG-4 Audio
        '.ogg',            # OGG audio
        '.opus'            # Opus audio codec
    ]
    
    VIDEO = [
        '.mp4',            # MPEG-4 Video
        '.avi',            # AVI Video
        '.mkv',            # Matroska Video
        '.mov',            # QuickTime Movie
        '.wmv',            # Windows Media Video
        '.flv',            # Flash Video
        '.webm'            # WebM Video
    ]
    
    ALL = (
        MICROSOFT_OFFICE + 
        TEXT_FILES + 
        DOCUMENTS + 
        COMPRESSED +
        AUDIO +
        VIDEO
    )
    
class MIMETypeGroups:
    """Nhóm các loại MIME type phổ biến"""
    
    # Audio MIME Types
    AUDIO = [
        'audio/mpeg',      # MP3
        'audio/wav',       # WAV
        'audio/flac',      # FLAC
        'audio/aac',       # AAC
        'audio/x-ms-wma',  # WMA
        'audio/mp4',       # M4A
        'audio/ogg',       # OGG
        'audio/opus'       # OPUS
    ]
    
    # Video MIME Types
    VIDEO = [
        'video/mp4',       # MP4
        'video/x-msvideo', # AVI
        'video/x-matroska',# MKV
        'video/quicktime', # MOV
        'video/x-ms-wmv',  # WMV
        'video/x-flv',     # FLV
        'video/webm'       # WebM
    ]
    
    # Document MIME Types
    DOCUMENTS = [
        'application/pdf',                 # PDF
        'application/msword',              # DOC
        'application/vnd.ms-word',         # DOC
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # DOCX
        'application/vnd.ms-excel',        # XLS
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',       # XLSX
        'application/vnd.ms-powerpoint',   # PPT
        'application/vnd.openxmlformats-officedocument.presentationml.presentation' # PPTX
    ]
    
    # Text MIME Types
    TEXT = [
        'text/plain',      # TXT
        'text/csv',        # CSV
        'text/markdown',   # MD
        'text/xml',        # XML
        'application/json' # JSON
    ]
    
    # Image MIME Types
    IMAGES = [
        'image/jpeg',      # JPG, JPEG
        'image/png',       # PNG
        'image/gif',       # GIF
        'image/bmp',       # BMP
        'image/webp'       # WebP
    ]
    
    # Compressed MIME Types
    COMPRESSED = [
        'application/zip',         # ZIP
        'application/x-rar-compressed', # RAR
        'application/x-7z-compressed',  # 7Z
        'application/gzip'         # GZIP
    ]
    
    ALL = (
        DOCUMENTS + 
        COMPRESSED +
        AUDIO +
        VIDEO +
        IMAGES +
        TEXT
    )

class FolderGoogleDrive:
    UPLOADS = {
        "project_id": "1nCPJqWcXug7CMgMk_7kXFNN0IjMVm8Xw",
        "transform_data": "1ZqtNTBFkTG-QI8Tuu3ekmPTEE6dHGsom"
    }
    
    DOWLOADS = {
        "audio_extract": "1N3B_P1wtxQOC0kGx5-AmCjWUs_7rNdS8",
        "image_extract": "17b7AtDk7RdGb1jr1WlV_d3msRU-WKP9b",
        "pdf_exam_extract": "1TmgkeQpbx3GqItz5DGYBA7kNvVf4W7cs",
    }

class GoogleDriveDownloader:
    def __init__(self, credentials_path='app/auth/credentials.json'):
        # Cấu hình logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename='drive_download.log'
        )
        self.logger = logging.getLogger(__name__)
        
        # Xác thực
        self.authenticate(credentials_path)

    def authenticate(self, credentials_path):
        """Xác thực và tạo dịch vụ Drive"""
        try:
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            
            creds = None
            if os.path.exists('app/auth/token_downloads.json'):
                creds = Credentials.from_authorized_user_file('app/auth/token_downloads.json', SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Lưu token
                with open('app/auth/token_downloads.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            self.logger.error(f"Lỗi xác thực: {e}")
            raise

    def download_file(
        self, 
        file_id: str, 
        local_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Tải xuống một file cụ thể
        
        :param file_id: ID file trên Google Drive
        :param local_path: Đường dẫn lưu file (tuỳ chọn)
        :return: Thông tin file đã tải
        """
        try:
            # Lấy thông tin file
            file_metadata = self.service.files().get(fileId=file_id).execute()
            filename = file_metadata.get('name', 'unknown_file')
            
            # Nếu không có local_path, sử dụng thư mục hiện tại
            if not local_path:
                local_path = os.path.join(os.getcwd(), filename)
            
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Tải file
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            download_attempts = 0
            max_attempts = 3
            
            while not done and download_attempts < max_attempts:
                try:
                    status, done = downloader.next_chunk()
                    
                    # Hiển thị tiến trình download
                    if status:
                        self.logger.info(
                            f"Đang tải xuống {filename}: {int(status.progress() * 100)}%"
                        )
                except HttpError as download_error:
                    download_attempts += 1
                    self.logger.warning(
                        f"Lỗi tải file {filename}. Thử lại lần {download_attempts}: {download_error}"
                    )
                    time.sleep(2 ** download_attempts)  # Backoff strategy
            
            if not done:
                raise Exception(f"Không thể tải file {filename} sau {max_attempts} lần thử")
            
            return {
                'filename': filename,
                'local_path': local_path,
                'file_id': file_id
            }
        
        except Exception as e:
            self.logger.error(f"Lỗi tải file {file_id}: {e}")
            return {}

    def download_files_from_folder(
        self, 
        folder_id: str, 
        local_download_dir: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        max_files: Optional[int] = None,
        file_size_limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Tải xuống nhiều file từ một thư mục
        
        :param folder_id: ID thư mục trên Google Drive
        :param local_download_dir: Thư mục lưu file (mặc định là thư mục hiện tại)
        :param file_types: Danh sách các loại file được phép
        :param max_files: Giới hạn số lượng file
        :param file_size_limit: Giới hạn kích thước file
        :return: Danh sách thông tin các file đã tải
        """
        try:
            # Sử dụng thư mục hiện tại nếu không có
            if not local_download_dir:
                local_download_dir = os.getcwd()
            
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(local_download_dir, exist_ok=True)
            
            # Truy vấn danh sách file
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'",
                fields="files(id, name, size, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            
            # Lọc và giới hạn file
            downloaded_files = []
            for file in files:
                # Kiểm tra số lượng file
                if max_files and len(downloaded_files) >= max_files:
                    break
                
                # Kiểm tra loại file
                file_extension = os.path.splitext(file['name'])[1].lower()
                if file_types and file_extension not in file_types:
                    continue
                
                # Kiểm tra kích thước file
                file_size = int(file.get('size', 0))
                if file_size_limit and file_size > file_size_limit:
                    self.logger.warning(f"Bỏ qua file {file['name']} - vượt quá giới hạn kích thước")
                    continue
                
                # Tải file
                local_path = os.path.join(local_download_dir, file['name'])
                download_result = self.download_file(
                    file_id=file['id'], 
                    local_path=local_path
                )
                
                if download_result:
                    downloaded_files.append(download_result)
            
            return downloaded_files
        
        except Exception as e:
            self.logger.error(f"Lỗi tải files từ thư mục: {e}")
            return []

class GoogleDriveBulkUploader:
    def __init__(self, credentials_path='app/auth/credentials.json'):
        """
        Khởi tạo kết nối Google Drive cho việc upload hàng loạt
        
        :param credentials_path: Đường dẫn file credentials
        """
        self.creds = None
        self.credentials_path = credentials_path
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.authenticate()

    def authenticate(self):
        """
        Xác thực tài khoản Google
        """
        try:
            # Nạp credentials từ file token
            if os.path.exists('app/auth/token_uploads.json'):
                with open('app/auth/token_uploads.json', 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Kiểm tra và làm mới credentials nếu cần
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Lưu lại credentials
                with open('app/auth/token_uploads.json', 'wb') as token:
                    pickle.dump(self.creds, token)
        except Exception as e:
            print(f"Lỗi xác thực: {e}")
            raise

    def upload_folder_to_drive(
        self, 
        local_folder_path: str, 
        drive_folder_id: Optional[str] = None,
        file_types: Optional[List[str]] = None
    ) -> List[dict]:
        """
        Upload toàn bộ files và folders từ thư mục local lên Google Drive
        
        :param local_folder_path: Đường dẫn thư mục local
        :param drive_folder_id: ID thư mục đích trên Google Drive (tuỳ chọn)
        :param file_types: Danh sách các loại file được phép upload (tuỳ chọn)
        :return: Danh sách thông tin các file và folder đã upload
        """
        try:
            # Khởi tạo dịch vụ Drive
            service = build('drive', 'v3', credentials=self.creds)
            
            # Danh sách các items đã upload
            uploaded_items = []
            
            def upload_recursive(local_path, parent_folder_id=None):
                """
                Hàm đệ quy để upload files và folders
                """
                for item in os.listdir(local_path):
                    # Đường dẫn đầy đủ của item
                    full_path = os.path.join(local_path, item)
                    
                    # Xử lý folder
                    if os.path.isdir(full_path):
                        # Tạo folder trên Google Drive
                        folder_metadata = {
                            'name': item,
                            'mimeType': 'application/vnd.google-apps.folder'
                        }
                        
                        # Thêm parent folder nếu có
                        if parent_folder_id:
                            folder_metadata['parents'] = [parent_folder_id]
                        
                        # Kiểm tra folder đã tồn tại chưa
                        query = f"name='{item}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                        if parent_folder_id:
                            query += f" and '{parent_folder_id}' in parents"
                        
                        existing_folders = service.files().list(
                            q=query,
                            spaces='drive',
                            fields='files(id)'
                        ).execute()
                        
                        # Nếu folder chưa tồn tại, tạo mới
                        if not existing_folders.get('files'):
                            new_folder = service.files().create(
                                body=folder_metadata,
                                fields='id'
                            ).execute()
                            folder_id = new_folder['id']
                        else:
                            # Sử dụng folder đã tồn tại
                            folder_id = existing_folders['files'][0]['id']
                        
                        # Thêm thông tin folder vào danh sách
                        uploaded_items.append({
                            'name': item,
                            'id': folder_id,
                            'type': 'folder'
                        })
                        
                        # Đệ quy upload nội dung của folder
                        upload_recursive(full_path, folder_id)
                    
                    # Xử lý file
                    elif os.path.isfile(full_path):
                        # Kiểm tra loại file nếu có filter
                        if file_types:
                            file_extension = os.path.splitext(item)[1].lower()
                            if file_extension not in file_types:
                                continue
                        
                        # Tìm kiếm file đã tồn tại
                        query = f"name='{item}' and trashed=false"
                        if parent_folder_id:
                            query += f" and '{parent_folder_id}' in parents"
                        
                        existing_files = service.files().list(
                            q=query,
                            spaces='drive',
                            fields='files(id)'
                        ).execute()
                        
                        # Chuẩn bị metadata file
                        file_metadata = {
                            'name': item
                        }
                        
                        # Thêm parent folder nếu có
                        if parent_folder_id:
                            file_metadata['parents'] = [parent_folder_id]
                        
                        # Tạo media upload
                        media = MediaFileUpload(
                            full_path, 
                            resumable=True
                        )
                        
                        try:
                            # Nếu file đã tồn tại, thực hiện update
                            if existing_files.get('files'):
                                existing_file_id = existing_files['files'][0]['id']
                                print(f"Ghi đè file: {item}")
                                file = service.files().update(
                                    fileId=existing_file_id,
                                    media_body=media,
                                    fields='id,name,webViewLink,webContentLink'
                                ).execute()
                            else:
                                # Nếu file chưa tồn tại, thực hiện tạo mới
                                print(f"Tạo mới file: {item}")
                                file = service.files().create(
                                    body=file_metadata,
                                    media_body=media,
                                    fields='id,name,webViewLink,webContentLink'
                                ).execute()
                            
                            # Lưu thông tin file
                            uploaded_items.append({
                                'name': file.get('name'),
                                'id': file.get('id'),
                                'type': 'file',
                                'web_view_link': file.get('webViewLink'),
                                'web_content_link': file.get('webContentLink')
                            })
                            
                            print(f"Đã xử lý: {item}")
                        
                        except Exception as upload_error:
                            print(f"Lỗi khi upload file {item}: {upload_error}")
            
            # Bắt đầu upload từ thư mục gốc
            upload_recursive(local_folder_path, drive_folder_id)
            
            return uploaded_items
        
        except Exception as e:
            print(f"Lỗi chung: {e}")
            return []



    def upload_single_file(
        self, 
        file_path: str, 
        drive_folder_id: Optional[str] = None
    ) -> Optional[dict]:
        """
        Upload một file đơn lẻ
        
        :param file_path: Đường dẫn file
        :param drive_folder_id: ID thư mục đích trên Drive
        :return: Thông tin file đã upload
        """
        try:
            # Khởi tạo dịch vụ Drive
            service = build('drive', 'v3', credentials=self.creds)
            
            # Chuẩn bị metadata file
            filename = os.path.basename(file_path)
            file_metadata = {
                'name': filename
            }
            
            # Thêm folder ID nếu được chỉ định
            if drive_folder_id:
                file_metadata['parents'] = [drive_folder_id]
            
            # Tạo media upload
            media = MediaFileUpload(
                file_path, 
                resumable=True
            )
            
            # Thực hiện upload
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,webContentLink'
            ).execute()
            
            # Trả về thông tin file
            return {
                'name': file.get('name'),
                'id': file.get('id'),
                'web_view_link': file.get('webViewLink'),
                'web_content_link': file.get('webContentLink')
            }
        
        except Exception as e:
            print(f"Lỗi upload: {e}")
            return None
        
def gg_downloads(folder_id):
    print(folder_id)
    downloader = GoogleDriveDownloader(credentials_path='app/auth/credentials.json')
    
    # Tải xuống tất cả các file 
    downloaded_files = downloader.download_files_from_folder(
        folder_id, 
        local_download_dir='app/data/downloads',
        file_types=FileTypeGroups.ALL # Tuỳ chọn: lọc theo loại file
    )
    
    for file_info in downloaded_files:
        print(f"Đã tải: {file_info['filename']}")
        print(f"Đường dẫn: {file_info['local_path']}")
        
def gg_uploads(drive_folder_id):
    # Khởi tạo uploader
    uploader = GoogleDriveBulkUploader(credentials_path='app/auth/credentials.json')
    
    # Upload toàn bộ file từ một thư mục
    uploaded_files = uploader.upload_folder_to_drive(
        local_folder_path='app/data/uploads',  # Thư mục chứa file cần upload
        drive_folder_id=drive_folder_id,
        file_types=FileTypeGroups.ALL,  # Tuỳ chọn: lọc theo định dạng file
        ignore_existing=True  # Bỏ qua file đã tồn tại
    )
    
    # In thông tin các file đã upload
    print("\nCác file đã upload:")
    for file_info in uploaded_files:
        print(f"Tên: {file_info['name']}")
        print(f"ID: {file_info['id']}")
        print(f"Link xem: {file_info['web_view_link']}\n")
    return uploaded_files

    # Hoặc upload file đơn lẻ
    # single_file = uploader.upload_single_file(
    #     file_path='uploads/example.mp3',
    #     drive_folder_id=drive_folder_id
    # )




# gg_downloads(FolderGoogleDrive.DOWLOADS["pdf_exam_extract"])
# gg_uploads(FolderGoogleDrive.UPLOADS["pdf_exam_transform"])
