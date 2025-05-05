from typing import List, Optional
from app.schemas.pdf import PDFCreate, PDFUpdate, PDF

class PDFService:
    def pdf_to_word(self, pdf_data: PDFCreate) -> PDF:
        return 1