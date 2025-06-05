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
    # list_exam_code = ["exam_pass_1", "exam_pass_2", "exam_pass_3", "exam_pass_4", "exam_pass_5", "exam_pass_6", "exam_pass_7", "exam_pass_8", "exam_pass_9", "exam_pass_10"]
    list_exam_code = ["exam_pass_11", "exam_pass_12", "exam_pass_13", "exam_pass_14", "exam_pass_15"]
    list_id_explain_advanced = common.get_all_file_names("app/data/questions")
    data_id = f'{body["id"]}_{body["exam_code_new"]}_{body["kind"]}'
    # print(data_id, list_id_explain_advanced)
    if data_id not in list_id_explain_advanced and body["exam_code_new"] in list_exam_code:
        return audio_service.split_audio(body)

