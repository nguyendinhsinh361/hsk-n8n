import asyncio
from typing import List, Optional
from app.schemas.ggdrive import GoogleDriveCreate, GoogleDriveUpdate, GoogleDrive
from app.utils.ggdrive import FileTypeGroups, FolderGoogleDrive, GoogleDriveBulkUploader, GoogleDriveDownloader

class GoogleDriveService:
    async def downloads_files_from_google_drive(self, folder_id):
        # Chuyển đổi folder_id sang giá trị thực
        folder_id_value = FolderGoogleDrive.DOWLOADS[folder_id.value]
        print(f"Downloading from folder: {folder_id_value}")
        
        # Khởi tạo downloader
        downloader = GoogleDriveDownloader(credentials_path='app/auth/credentials.json')
        
        # Sử dụng asyncio.to_thread để chạy download không blocking
        # downloaded_files = await asyncio.to_thread(
        #     downloader.download_files_from_folder,
        #     folder_id=folder_id_value, 
        #     local_download_dir='app/data/downloads',
        #     file_types=FileTypeGroups.ALL
        # )
        downloaded_files = await asyncio.to_thread(
            downloader.download_folder_structure,
            folder_id=folder_id_value, 
            local_base_path='app/data/downloads',
            file_types=FileTypeGroups.ALL
        )
        
        # Log chi tiết file đã tải
        if not downloaded_files:
            print("Không có file nào được tải xuống.")
            return []
        
        # In thông tin chi tiết file
        for file_info in downloaded_files:
            print(f"Đã tải: {file_info.get('filename', 'Không xác định')}")
            print(f"Đường dẫn: {file_info.get('local_path', 'Không xác định')}")
        
        return downloaded_files
    
    async def download_folder_structure_google_drive(self, folder_id):
        # Chuyển đổi folder_id sang giá trị thực
        folder_id_value = FolderGoogleDrive.DOWLOADS[folder_id.value]
        print(f"Downloading from folder: {folder_id_value}")
        
        # Khởi tạo downloader
        downloader = GoogleDriveDownloader(credentials_path='app/auth/credentials.json')
        
        downloaded_files = await asyncio.to_thread(
            downloader.download_folder_structure,
            folder_id=folder_id_value, 
            local_base_path='app/data/downloads',
            file_types=FileTypeGroups.ALL
        )
        
        return downloaded_files
    
    async def uploads_files_to_google_drive(self, folder_id) -> GoogleDrive:
        # Khởi tạo uploader
        folder_id_value = FolderGoogleDrive.UPLOADS[folder_id.value]
        print(f"Uploads to folder: {folder_id_value}")
        uploader = GoogleDriveBulkUploader(credentials_path='app/auth/credentials.json')
        
        # Sử dụng asyncio.to_thread để chạy upload không blocking
        uploaded_files = await asyncio.to_thread(
            uploader.upload_folder_to_drive,
            local_folder_path='app/data/uploads',  # Thư mục chứa file cần upload
            drive_folder_id=folder_id_value,
            file_types=FileTypeGroups.ALL,  # Tuỳ chọn: lọc theo định dạng file
        )
        
        # In thông tin các file đã upload
        print("\nCác file đã upload:")
        for file_info in uploaded_files:
            print(f"Tên: {file_info.get('name', 'Không xác định')}")
            print(f"ID: {file_info.get('id', 'Không xác định')}")
            print(f"Link xem: {file_info.get('web_view_link', 'Không có link')}\n")
        
        return uploaded_files
