from typing import Optional
from pydantic import BaseModel

class AudioBase(BaseModel):
    title: str
    description: Optional[str] = None

class AudioCreate(AudioBase):
    pass

class AudioUpdate(AudioBase):
    title: Optional[str] = None

class Audio(AudioBase):
    id: int
    owner_id: int
    
    class Config:
        from_attributes = True
