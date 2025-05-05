from app.api.enums.telegram import CommandTelegramEnum, ChatIDTelegramEnum
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.services.telegram_service import TelegramService

router = APIRouter()
telegram_service = TelegramService()

@router.post("/command", 
            #  response_model=Telegram, 
             status_code=status.HTTP_201_CREATED
             )
async def push_command_to_telegram(
    command_id: CommandTelegramEnum = Query(..., description="Please choose command_id\n\n"),
    chat_id: ChatIDTelegramEnum = Query(..., description="Please choose chat_id\n\n")
    ):
    return await telegram_service.push_command_to_telegram(command_id, chat_id)

