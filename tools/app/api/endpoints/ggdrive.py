from app.api.enums.ggdrive import FolderIdDownloadsEnum, FolderIdUploadsEnum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.schemas.ggdrive import GoogleDrive, GoogleDriveCreate, GoogleDriveUpdate
from app.services.ggdrive_service import GoogleDriveService

router = APIRouter()
ggdrive_service = GoogleDriveService()

@router.post("/uploads", 
            #  response_model=GoogleDrive, 
             status_code=status.HTTP_201_CREATED
             )
async def uploads_files_to_goolge_drive(folder_id: FolderIdUploadsEnum = Query(..., description="Please choose folder_id want to uploads from local\n\n")):
    return await ggdrive_service.uploads_files_to_google_drive(folder_id)

@router.get("/downloads", 
            # response_model=GoogleDrive
            )
async def downloads_files_from_google_drive(folder_id: FolderIdDownloadsEnum = Query(..., description="Please choose folder_id want to downloads from google drive\n\n")):
    ggdrive = await ggdrive_service.downloads_files_from_google_drive(folder_id)
    if ggdrive is None:
        raise HTTPException(status_code=404, detail="folder_id not found")
    return ggdrive
