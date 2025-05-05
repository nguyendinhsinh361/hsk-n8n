from typing import Optional
from pydantic import BaseModel

class PDFBase(BaseModel):
    pdfname: str

class PDFCreate(PDFBase):
    password: str

class PDFUpdate(PDFBase):
    password: Optional[str] = None

class PDFInDB(PDFBase):
    id: int
    is_active: bool = True
    
    class Config:
        from_attributes = True

class PDF(PDFBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    PDFname: Optional[str] = None
