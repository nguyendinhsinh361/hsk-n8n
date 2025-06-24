import json
import os
from datetime import datetime
import re
from typing import List, Optional
import ast

from pydantic import conset
from app.cmd.split_audio import EnhancedAudioSplitter, download_from_drive

class AudioService:
    def __init__(self):
        self.json_output_path = "app/data/mapping/mapping.json"
        # Đảm bảo thư mục mapping tồn tại
        os.makedirs(os.path.dirname(self.json_output_path), exist_ok=True)
    
    def check_and_fix_time_format(self, input_string):
        input_string = re.sub('）', ')', input_string.strip())
        # Mẫu regex để kiểm tra format ("HH:MM:SS", "HH:MM:SS")
        correct_pattern = r'\("(\d{2}:\d{2}:\d{2})", "(\d{2}:\d{2}:\d{2})"\)'
        
        # Kiểm tra xem đã đúng format chưa
        if re.match(correct_pattern, input_string):
            # print(f"Format đúng: {input_string}")
            return input_string
        
        # Trích xuất các giá trị thời gian từ chuỗi đầu vào
        time_pattern = r'"(\d{2}:\d{2}:\d{2})'
        times = re.findall(time_pattern, input_string)
        
        if len(times) == 2:
            # Format đúng: ("00:08:07", "00:08:25")
            correct_format = f'("{times[0]}", "{times[1]}")'
            # print(f"Format sai, đã sửa: {input_string} -> {correct_format}")
            return correct_format
        
        # print(f"Không thể sửa format: {input_string}")
        return input_string
    
    def split_audio(self, body):
        # Kiểm tra xem file JSON đã tồn tại chưa
        results = []
        existing_mapping = {}
        audio_mapping = []
        if os.path.exists(self.json_output_path):
            try:
                with open(self.json_output_path, 'r', encoding='utf-8') as json_file:
                    audio_mapping = json.load(json_file)
                    # Tạo dictionary để dễ dàng tìm kiếm theo local_path
                    existing_mapping = {item["local_path"]: item for item in audio_mapping}
            except Exception as e:
                print(f"Lỗi khi đọc file JSON hiện có: {str(e)}")
                # Nếu có lỗi, khởi tạo lại danh sách trống
                audio_mapping = []
        question_audios = [{
            "field": "G_audio",
            "key": f'{body["id"]}_{body["exam_code_new"]}_{body["kind"]}_G_audio',
            "link": body["G_audio"],
            "timestamps": self.check_and_fix_time_format(body["G_audio_time_split"])
        }]
        for index in range(5):
            question_audios.append({
                "field": f'Q_audio_{index+1}',
                "key": f'{body["id"]}_{body["exam_code_new"]}_{body["kind"]}_Q_audio_{index+1}',
                "link": body[f"Q_audio_{index+1}"],
                "timestamps": self.check_and_fix_time_format(body[f"Q_audio_{index+1}_time_split"])
            })
        
        for index in range(5):
            question_audios.append({
                "field": f'A_audio_{index+1}',
                "key": f'{body["id"]}_{body["exam_code_new"]}_{body["kind"]}_A_audio_{index+1}',
                "link": body[f"A_audio_{index+1}"],
                "timestamps": self.check_and_fix_time_format(body[f"A_audio_{index+1}_time_split"])
            })
        
        question_audios_raw = [
        {
            "field": item["field"],
            "key": item["key"],
            "link": item["link"],
            "timestamps": [ast.literal_eval(item['timestamps'])],
        } for item in question_audios 
            if item['link'] and item['timestamps']
        ]
        
        # Thiết lập thư mục đầu ra
        folder_path = None
        if folder_path is None:
            folder_path = "app/data"
        
        # Tạo các thư mục cần thiết
        downloads_folder = os.path.join(folder_path, "downloads/audio_extract/")
        output_folder = os.path.join(folder_path, "split/")
        os.makedirs(downloads_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        
        # Xử lý file âm thanh
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Tạo dictionary để lưu trữ link và đường dẫn file đã tải
        downloaded_links = {}
        
        for tmp in question_audios_raw:
            if tmp["link"] is not None:
                # Kiểm tra xem link này đã được tải trước đó chưa
                if tmp["link"] in downloaded_links:
                    audio_path = downloaded_links[tmp["link"]]
                    print(f"Sử dụng file đã tải: {audio_path}")
                else:
                    # Lấy tên file từ link hoặc sử dụng tên mặc định
                    file_name = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                    
                    # Tải file từ Google Drive
                    print(f"Đang tải file từ Google Drive...")
                    audio_path = download_from_drive(tmp["link"], downloads_folder)
                    print(f"Đã tải file thành công: {audio_path}")
                    
                    # Lưu vào dictionary để tái sử dụng
                    downloaded_links[tmp["link"]] = audio_path
            else:
                raise ValueError("Cần cung cấp audio_link")
            
            # print(1111, audio_path)
            # Khởi tạo splitter
            splitter = EnhancedAudioSplitter(audio_path)

            # Cắt audio
            saved_files = splitter.split_audio(
                timestamps=tmp["timestamps"],
                file_format='mp3', 
                filename=tmp["key"],
                output_directory=output_folder
            )
            
            # Thêm thông tin vào kết quả
            for i, segment_file in enumerate(saved_files):
                if i < len(tmp["timestamps"]):
                    # Kiểm tra xem segment_file đã tồn tại trong mapping chưa
                    if segment_file in existing_mapping:
                        # Cập nhật bản ghi hiện có
                        existing_item = existing_mapping[segment_file]
                        existing_item["original_link"] = tmp["link"]
                        existing_item["timestamp"] = str(tmp["timestamps"][i])
                        existing_item["key"] = tmp["key"]  # Thêm trường key
                        # Lưu giá trị updated_at hiện tại vào latest_updated_at
                        if "updated_at" in existing_item:
                            existing_item["latest_updated_at"] = existing_item["updated_at"]
                        # Cập nhật updated_at thành thời gian hiện tại
                        existing_item["updated_at"] = current_time
                    else:
                        # Tạo bản ghi mới
                        new_item = {
                            "key": tmp["key"],
                            "original_link": tmp["link"],
                            "local_path": segment_file,
                            "timestamp": str(tmp["timestamps"][i]),
                            "created_at": current_time,
                            "updated_at": current_time,
                            "latest_updated_at": None  # Ban đầu là None vì chưa có cập nhật trước đó
                        }
                        audio_mapping.append(new_item)
                        existing_mapping[segment_file] = new_item
            
            results.extend(saved_files)
        
        # Lưu kết quả vào file JSON
        with open(self.json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(audio_mapping, json_file, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu thông tin ánh xạ audio vào file: {self.json_output_path}")
        return {
            tmp["field"]: f'{tmp["key"]}.mp3' if tmp["link"] and tmp["timestamps"] else None for tmp in question_audios
        }

    def split_single_audio(self, body):
        """
        Split a single audio file based on provided timestamps
        
        :param body: Dictionary containing:
            - audio_link: URL to the audio file (Google Drive link)
            - timestamps: List of timestamp pairs in format [("HH:MM:SS", "HH:MM:SS"), ...]
            - key: Unique identifier for the audio segments
            - output_directory: (Optional) Directory to save the split audio files
        :return: Dictionary with paths to the split audio files
        """
        # Kiểm tra xem file JSON đã tồn tại chưa
        existing_mapping = {}
        audio_mapping = []
        
        if os.path.exists(self.json_output_path):
            try:
                with open(self.json_output_path, 'r', encoding='utf-8') as json_file:
                    audio_mapping = json.load(json_file)
                    # Tạo dictionary để dễ dàng tìm kiếm theo local_path
                    existing_mapping = {item["local_path"]: item for item in audio_mapping}
            except Exception as e:
                print(f"Lỗi khi đọc file JSON hiện có: {str(e)}")
                # Nếu có lỗi, khởi tạo lại danh sách trống
                audio_mapping = []
        
        # Thiết lập thư mục đầu ra
        output_directory = body.get("output_directory", "app/data/split/")
        downloads_folder = "app/data/downloads/audio_extract/"
        
        # Tạo các thư mục cần thiết
        os.makedirs(downloads_folder, exist_ok=True)
        os.makedirs(output_directory, exist_ok=True)
        
        # Xử lý timestamps
        timestamps = body["timestamps"]
        if isinstance(timestamps, str):
            try:
                # Nếu timestamps là chuỗi, thử chuyển đổi thành list
                timestamps = ast.literal_eval(timestamps)
            except:
                # Nếu không thể chuyển đổi, áp dụng hàm check_and_fix_time_format
                timestamps = [ast.literal_eval(self.check_and_fix_time_format(timestamps))]
        
        # Tải file từ Google Drive
        audio_link = body["audio_link"]
        key = body["key"]
        
        print(f"Đang tải file từ Google Drive...")
        audio_path = download_from_drive(audio_link, downloads_folder)
        print(f"Đã tải file thành công: {audio_path}")
        
        # Khởi tạo splitter
        splitter = EnhancedAudioSplitter(audio_path)
        
        # Cắt audio
        saved_files = splitter.split_audio(
            timestamps=timestamps,
            file_format='mp3', 
            filename=key,
            output_directory=output_directory
        )
        
        # Cập nhật mapping
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Thêm thông tin vào kết quả
        for i, segment_file in enumerate(saved_files):
            if i < len(timestamps):
                # Kiểm tra xem segment_file đã tồn tại trong mapping chưa
                if segment_file in existing_mapping:
                    # Cập nhật bản ghi hiện có
                    existing_item = existing_mapping[segment_file]
                    existing_item["original_link"] = audio_link
                    existing_item["timestamp"] = str(timestamps[i])
                    existing_item["key"] = key
                    # Lưu giá trị updated_at hiện tại vào latest_updated_at
                    if "updated_at" in existing_item:
                        existing_item["latest_updated_at"] = existing_item["updated_at"]
                    # Cập nhật updated_at thành thời gian hiện tại
                    existing_item["updated_at"] = current_time
                else:
                    # Tạo bản ghi mới
                    new_item = {
                        "key": key,
                        "original_link": audio_link,
                        "local_path": segment_file,
                        "timestamp": str(timestamps[i]),
                        "created_at": current_time,
                        "updated_at": current_time,
                        "latest_updated_at": None  # Ban đầu là None vì chưa có cập nhật trước đó
                    }
                    audio_mapping.append(new_item)
                    existing_mapping[segment_file] = new_item
        
        # Lưu kết quả vào file JSON
        with open(self.json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(audio_mapping, json_file, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu thông tin ánh xạ audio vào file: {self.json_output_path}")
        
        # Trả về đường dẫn đến file đã lưu
        return {
            "key": key,
            "audio_file": f"{key}.mp3",
            "file_path": saved_files[0] if saved_files else None,
            "success": True
        }
