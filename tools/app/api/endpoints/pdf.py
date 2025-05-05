from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.pdf import PDF, PDFCreate, PDFUpdate
from app.services.pdf_service import PDFService

router = APIRouter()
pdf_service = PDFService()

@router.post("/", response_model=PDF, status_code=status.HTTP_201_CREATED)
async def pdf_to_word_tool(pdf: PDFCreate):
    return pdf_service.pdf_to_word(pdf)

