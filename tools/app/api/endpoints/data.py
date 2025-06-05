from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.services.data_service import DataService

router = APIRouter()
data_service = DataService()


@router.post("/prepare", 
             status_code=status.HTTP_201_CREATED
             )
async def create_data_from_format(body: Dict[str, Any]):
    return data_service.create_data(body)

@router.post("/merge-question-exam", 
             status_code=status.HTTP_201_CREATED
             )
async def merge_question_exam():
    return data_service.merge_question_exam()

