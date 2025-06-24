from typing import Optional, List, Union, Tuple, Any
from pydantic import BaseModel, Field

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

class AudioSplitRequest(BaseModel):
    audio_link: str = Field(..., description="URL to the audio file (Google Drive link)")
    timestamps: List[Tuple[str, str]] = Field(..., description="List of timestamp pairs in format [('HH:MM:SS', 'HH:MM:SS'), ...]")
    key: str = Field(..., description="Unique identifier for the audio segments")
    output_directory: Optional[str] = Field(None, description="Optional directory to save the split audio files")

class AudioSplitResponse(BaseModel):
    key: str
    audio_file: str
    file_path: Optional[str]
    success: bool
