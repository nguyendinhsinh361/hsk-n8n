import json
import os
from datetime import datetime
from typing import List, Optional
import ast
from PIL import Image
import os
import re
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from pydantic import conset

class ImageService:
    def __init__(self):
        self.abc = ""
    
    def extract_file_id_from_drive_link(self, link):
        """
        Trích xuất ID file từ link Google Drive
        
        :param link: Link Google Drive
        :return: ID file
        """
        # Mẫu URL thông thường: https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
        if match:
            return match.group(1)
        
        # Mẫu URL chia sẻ: https://drive.google.com/open?id=FILE_ID
        match = re.search(r'id=([a-zA-Z0-9_-]+)', link)
        if match:
            return match.group(1)
        
        raise ValueError(f"Không thể trích xuất ID file từ link: {link}")

    def download_from_drive(self, drive_links, output_path):
        """
        Tải nhiều file hình ảnh từ Google Drive sử dụng OAuth credentials
        
        :param drive_links: Danh sách các link Google Drive (chuỗi với mỗi link trên một dòng)
        :param output_path: Thư mục để lưu các file
        :return: Danh sách đường dẫn đến các file đã tải
        """
        # Tách các link thành danh sách
        links = [link.strip() for link in drive_links.split('\n') if link.strip()]
        
        # Thiết lập phạm vi quyền truy cập
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        
        creds = None
        # Token đã lưu trước đó
        token_path = 'app/auth/token_downloads_images.json'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Nếu không có credentials hợp lệ, thì yêu cầu người dùng đăng nhập
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Sử dụng credentials.json để xác thực
                flow = InstalledAppFlow.from_client_secrets_file(
                    'app/auth/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Lưu credentials để sử dụng lần sau
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Xây dựng service
        service = build('drive', 'v3', credentials=creds)
        
        # Tạo thư mục chứa file nếu chưa tồn tại
        os.makedirs(output_path, exist_ok=True)
        
        downloaded_files = []
        
        # Tải từng file
        for i, link in enumerate(links):
            try:
                # Trích xuất ID file từ link
                file_id = self.extract_file_id_from_drive_link(link)
                
                # Lấy thông tin file để biết tên file gốc
                file_metadata = service.files().get(fileId=file_id, fields="name").execute()
                file_name = file_metadata.get('name', f"image_{file_id}")
                
                # Đảm bảo file_name có phần mở rộng hình ảnh
                if not any(file_name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    file_name += '.jpg'  # Mặc định là jpg nếu không có phần mở rộng
                    
                file_output_path = os.path.join(output_path, file_name)
                
                # Tải file
                request = service.files().get_media(fileId=file_id)
                
                with open(file_output_path, 'wb') as f:
                    downloader = MediaIoBaseDownload(f, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"File {i+1}/{len(links)} - {file_name}: Đã tải {int(status.progress() * 100)}%")
                
                downloaded_files.append(file_output_path)
                print(f"Đã tải file thành công: {file_output_path}")
                
            except Exception as e:
                print(f"Lỗi khi tải file từ link {link}: {str(e)}")
        
        print(f"Đã tải {len(downloaded_files)}/{len(links)} file thành công")
        return downloaded_files

    def convert_to_webp(self, input_path, output_path=None, target_kb=50, quality_start=80, min_quality=10, min_scale=0.3):
        """
        Chuyển đổi hình ảnh sang định dạng WebP với kích thước mục tiêu
        
        :param input_path: Đường dẫn đến file hình ảnh đầu vào
        :param output_path: Đường dẫn đến file đầu ra (nếu None, sẽ tạo trong cùng thư mục với đuôi .webp)
        :param target_kb: Kích thước mục tiêu tính bằng KB
        :param quality_start: Chất lượng ban đầu (1-100)
        :param min_quality: Chất lượng tối thiểu trước khi thay đổi kích thước
        :param min_scale: Tỷ lệ thu nhỏ tối thiểu
        :return: Kích thước cuối cùng (KB) và đường dẫn đến file đầu ra
        """
        # Mở ảnh
        img = Image.open(input_path)
        
        # Lấy kích thước ban đầu
        original_size = os.path.getsize(input_path) // 1024
        print(f"Kích thước ảnh ban đầu: {original_size} KB")
        
        # Nếu không có output_path, tạo trong cùng thư mục với đuôi .webp
        if output_path is None:
            input_dir = os.path.dirname(input_path)
            input_filename = os.path.basename(input_path)
            input_name = os.path.splitext(input_filename)[0]
            output_path = os.path.join(input_dir, f"{input_name}.webp")
        else:
            # Đảm bảo output_path có đuôi .webp
            output_path = os.path.splitext(output_path)[0] + ".webp"
        # return 0, output_path
        
        # Tạo thư mục đầu ra nếu chưa tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Nếu ảnh đầu vào đã nhỏ hơn kích thước mục tiêu, chỉ cần chuyển đổi định dạng
        if original_size <= target_kb:
            img.save(output_path, format="WEBP", quality=quality_start)
            final_size = os.path.getsize(output_path) // 1024
            print(f"Ảnh đã nhỏ hơn mục tiêu. Kích thước sau khi chuyển đổi: {final_size} KB")
            return final_size, output_path
        
        # Thử các mức chất lượng khác nhau
        quality = quality_start
        current_size = original_size
        
        while True:
            img.save(output_path, format="WEBP", quality=quality)
            
            current_size = os.path.getsize(output_path) // 1024
            print(f"Thử với chất lượng {quality}: {current_size} KB")
            
            if current_size <= target_kb or quality <= min_quality:
                print(f"Kích thước ảnh sau khi chuyển đổi sang WebP: {current_size} KB với chất lượng {quality}")
                break
                
            quality -= 10
        
        # Nếu vẫn lớn hơn kích thước mục tiêu, thay đổi kích thước vật lý
        if current_size > target_kb:
            width, height = img.size
            scale_factor = 0.9  # Giảm 10% mỗi lần
            
            while current_size > target_kb and scale_factor >= min_scale:
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                resized_img.save(output_path, format="WEBP", quality=quality)
                
                current_size = os.path.getsize(output_path) // 1024
                print(f"Thay đổi kích thước xuống {scale_factor:.1f}x ({new_width}x{new_height}): {current_size} KB")
                
                if current_size <= target_kb:
                    break
                    
                scale_factor -= 0.1
        
        print(f"Kích thước cuối cùng: {current_size} KB")
        return current_size, output_path

    def batch_convert_from_drive_links(self, drive_links_string, download_dir="app/data/downloads/image_extract", output_dir="app/data/resize", target_kb=50):
        if not drive_links_string.strip():
            return None
        """
        Tải nhiều hình ảnh từ Google Drive và chuyển đổi sang định dạng WebP
        
        :param drive_links_string: Chuỗi chứa các link Google Drive (mỗi link trên một dòng)
        :param download_dir: Thư mục để lưu các file tải về
        :param output_dir: Thư mục để lưu các file WebP
        :param target_kb: Kích thước mục tiêu tính bằng KB
        :return: Danh sách các đường dẫn đến file WebP đã chuyển đổi
        """
        print(f"Bắt đầu tải các file từ Google Drive...")
        
        # Tạo thư mục tải về và thư mục đầu ra
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Tải các file từ Google Drive
        downloaded_files = self.download_from_drive(drive_links_string, download_dir)
        
        if not downloaded_files:
            print("Không có file nào được tải về từ Google Drive!")
            return []
        
        print(f"\nĐã tải xong {len(downloaded_files)} file. Bắt đầu chuyển đổi sang WebP...")
        
        # Chuyển đổi các file đã tải về sang WebP
        converted_files = []
        
        for i, input_file in enumerate(downloaded_files):
            try:
                # Tạo đường dẫn đầu ra
                filename = os.path.basename(input_file)
                name = os.path.splitext(filename)[0]
                output_path = os.path.join(output_dir, f"{name}.webp")
                
                print(f"\nChuyển đổi file {i+1}/{len(downloaded_files)}: {filename}")
                _, output_file = self.convert_to_webp(input_file, output_path, target_kb)
                converted_files.append(output_file)
                
            except Exception as e:
                print(f"Lỗi khi chuyển đổi file {input_file}: {str(e)}")
        
        print(f"\nĐã hoàn thành! Chuyển đổi thành công {len(converted_files)}/{len(downloaded_files)} file.")
        print("\nCác file WebP đã được lưu tại:")
        for file in converted_files:
            print(f"- {os.path.abspath(file)}")
        
        return converted_files
    
    def reize_memory_image(self, body):
        question_images = [{
            "field": "G_image",
            "value": self.batch_convert_from_drive_links(body["G_image"]),
            "link": body["G_image"],
        }]
        for index in range(5):
            question_images.append({
                "field": f'Q_image_{index+1}',
                "value": self.batch_convert_from_drive_links(body[f"Q_image_{index+1}"]),
                "link": body[f"Q_image_{index+1}"],
            })
        
        for index in range(5):
            question_images.append({
                "field": f'A_image_{index+1}',
                "value": self.batch_convert_from_drive_links(body[f"A_image_{index+1}"]),
                "link": body[f"A_image_{index+1}"],
            })
            
        return {
            tmp["field"]: [tmp_img.split("/")[-1] for tmp_img in tmp["value"]] if tmp["value"] and tmp["link"] else None for tmp in question_images
        }
        
    def resize_uploaded_image(self, file_path, output_dir="app/data/uploads/resized", target_kb=100, 
                              width=None, height=None, quality_start=85, min_quality=20, min_scale=0.3):
        """
        Thay đổi kích thước một hình ảnh đã tải lên
        
        :param file_path: Đường dẫn đến file hình ảnh đầu vào
        :param output_dir: Thư mục để lưu file đã resize
        :param target_kb: Kích thước mục tiêu tính bằng KB
        :param width: Chiều rộng mới (nếu None, giữ tỷ lệ dựa trên chiều cao)
        :param height: Chiều cao mới (nếu None, giữ tỷ lệ dựa trên chiều rộng)
        :param quality_start: Chất lượng ban đầu (1-100)
        :param min_quality: Chất lượng tối thiểu trước khi thay đổi kích thước
        :param min_scale: Tỷ lệ thu nhỏ tối thiểu
        :return: Đường dẫn đến file đã resize và thông tin kích thước
        """
        try:
            # Đảm bảo thư mục đầu ra tồn tại
            os.makedirs(output_dir, exist_ok=True)
            
            # Mở ảnh
            img = Image.open(file_path)
            
            # Lấy kích thước ban đầu
            original_size = os.path.getsize(file_path) // 1024
            original_width, original_height = img.size
            
            # Tạo đường dẫn đầu ra
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}.webp")
            
            # Nếu cần resize cụ thể
            if width or height:
                new_width = width or int(original_width * height / original_height)
                new_height = height or int(original_height * width / original_width)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Nếu ảnh đầu vào đã nhỏ hơn kích thước mục tiêu và không cần resize cụ thể
            if original_size <= target_kb and not (width or height):
                img.save(output_path, format="WEBP", quality=quality_start)
                final_size = os.path.getsize(output_path) // 1024
                return {
                    'path': output_path,
                    'original_size': original_size,
                    'resized_size': final_size,
                    'original_dimensions': f"{original_width}x{original_height}",
                    'resized_dimensions': f"{img.width}x{img.height}"
                }
            
            # Thử các mức chất lượng khác nhau
            quality = quality_start
            current_size = original_size
            
            while True:
                img.save(output_path, format="WEBP", quality=quality)
                
                current_size = os.path.getsize(output_path) // 1024
                
                if current_size <= target_kb or quality <= min_quality:
                    break
                    
                quality -= 10
            
            # Nếu vẫn lớn hơn kích thước mục tiêu, thay đổi kích thước vật lý
            if current_size > target_kb and not (width or height):
                current_width, current_height = img.size
                scale_factor = 0.9  # Giảm 10% mỗi lần
                
                while current_size > target_kb and scale_factor >= min_scale:
                    new_width = int(current_width * scale_factor)
                    new_height = int(current_height * scale_factor)
                    
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    resized_img.save(output_path, format="WEBP", quality=quality)
                    
                    current_size = os.path.getsize(output_path) // 1024
                    
                    if current_size <= target_kb:
                        img = resized_img
                        break
                        
                    scale_factor -= 0.1
            
            # Lấy kích thước cuối cùng của ảnh đã resize
            final_img = Image.open(output_path)
            
            return {
                'path': output_path,
                'original_size': original_size,
                'resized_size': current_size,
                'original_dimensions': f"{original_width}x{original_height}",
                'resized_dimensions': f"{final_img.width}x{final_img.height}",
                'quality': quality
            }
            
        except Exception as e:
            print(f"Lỗi khi resize ảnh: {str(e)}")
            raise e
