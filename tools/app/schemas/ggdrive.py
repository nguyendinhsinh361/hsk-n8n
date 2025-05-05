from typing import Optional
from pydantic import BaseModel

class GoogleDriveBase(BaseModel):
    title: str
    description: Optional[str] = None

class GoogleDriveCreate(GoogleDriveBase):
    pass

class GoogleDriveUpdate(GoogleDriveBase):
    title: Optional[str] = None

class GoogleDrive(GoogleDriveBase):
    id: int
    owner_id: int
    
    class Config:
        from_attributes = True
