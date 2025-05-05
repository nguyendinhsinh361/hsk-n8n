from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.services.audio_service import AudioService
from app.utils import common

router = APIRouter()
audio_service = AudioService()


@router.post("/split", 
             status_code=status.HTTP_201_CREATED
             )
async def split_audio(body: Dict[str, Any]):
    list_id_explain_advanced = common.get_all_file_names("app/data/questions")
    data_id = f'{body["id"]}_{body["exam_code"]}_{body["kind"]}'
    print(data_id, list_id_explain_advanced)
    if data_id not in list_id_explain_advanced:
        return audio_service.split_audio(body)

