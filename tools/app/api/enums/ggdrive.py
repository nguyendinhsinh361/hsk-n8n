from enum import Enum


class FolderIdDownloadsEnum(str, Enum):
    audio_extract = "audio_extract"
    image_extract = "image_extract"
    pdf_exam_extract = "pdf_exam_extract"


class FolderIdUploadsEnum(str, Enum):
    audio_transform = "audio_transform"
    image_transform = "image_transform"
    transform_data = "transform_data"
    