from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.services.image_service import ImageService
from app.utils import common

router = APIRouter()
image_service = ImageService()


@router.post("/resize-memory", 
             status_code=status.HTTP_201_CREATED
             )
async def reize_memory_image_tool(body: Dict[str, Any]):
    list_id_explain_advanced = common.get_all_file_names("app/data/questions")
    data_id = f'{body["id"]}_{body["exam_code"]}_{body["kind"]}'
    print(data_id, list_id_explain_advanced)
    if data_id not in list_id_explain_advanced:
        return image_service.reize_memory_image(body)

