from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict, Any, Optional

from app.services.image_service import ImageService
from app.utils import common
import os
import uuid
import shutil

router = APIRouter()
image_service = ImageService()


@router.post("/resize-memory", 
             status_code=status.HTTP_201_CREATED
             )
async def reize_memory_image_tool(body: Dict[str, Any]):
    # list_exam_code = ["exam_pass_1", "exam_pass_2", "exam_pass_3", "exam_pass_4", "exam_pass_5", "exam_pass_6", "exam_pass_7", "exam_pass_8", "exam_pass_9", "exam_pass_10"]
    list_exam_code = ["exam_pass_11", "exam_pass_12", "exam_pass_13", "exam_pass_14", "exam_pass_15"]
    list_id_explain_advanced = common.get_all_file_names("app/data/questions")
    data_id = f'{body["id"]}_{body["exam_code_new"]}_{body["kind"]}'
    # print(data_id, list_id_explain_advanced)
    if data_id not in list_id_explain_advanced and body["exam_code_new"] in list_exam_code:
        return image_service.reize_memory_image(body)

@router.post("/resize-image",
            status_code=status.HTTP_200_OK,
            summary="Resize an uploaded image",
            description="Upload an image file and resize it with optional parameters")
async def resize_image(
    file: UploadFile = File(...),
    target_kb: Optional[int] = Form(100),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    quality: Optional[int] = Form(85)
):
    """
    Nhận một file hình ảnh và thay đổi kích thước của nó
    
    - **file**: File hình ảnh cần resize
    - **target_kb**: Kích thước mục tiêu tính bằng KB (mặc định: 100)
    - **width**: Chiều rộng mới (nếu None, giữ tỷ lệ dựa trên chiều cao)
    - **height**: Chiều cao mới (nếu None, giữ tỷ lệ dựa trên chiều rộng)
    - **quality**: Chất lượng ban đầu (1-100, mặc định: 85)
    """
    try:
        # Kiểm tra loại file
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in valid_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File không được hỗ trợ. Các loại file hỗ trợ: {', '.join(valid_extensions)}"
            )
        
        # Tạo thư mục tạm nếu chưa tồn tại
        temp_dir = "app/data/uploads/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Tạo tên file ngẫu nhiên để tránh trùng lặp
        temp_file_name = file.filename
        temp_file_path = os.path.join(temp_dir, temp_file_name)
        
        # Lưu file tải lên vào thư mục tạm
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Resize hình ảnh
        result = image_service.resize_uploaded_image(
            file_path=temp_file_path,
            target_kb=target_kb,
            width=width,
            height=height,
            quality_start=quality
        )
        
        # Xóa file tạm sau khi resize
        try:
            os.remove(temp_file_path)
        except:
            pass  # Bỏ qua lỗi nếu không thể xóa file
        
        # Lấy đường dẫn file tương đối
        result['relative_path'] = os.path.relpath(result['path'])
        result['filename'] = os.path.basename(result['path'])
        
        return result
        
    except Exception as e:
        # Đảm bảo xóa file tạm nếu có lỗi
        try:
            if 'temp_file_path' in locals():
                os.remove(temp_file_path)
        except:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý file: {str(e)}"
        )

