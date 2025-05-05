import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import audio, ggdrive, pdf, image, data
from app.core.exceptions import CustomException

app = FastAPI(
    title="API SUPPORT FOR N8N",
    description="More Tool",
    version="0.1.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong môi trường production, hãy giới hạn nguồn gốc
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Xử lý ngoại lệ toàn cục
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

# Bao gồm các router
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF TOOL"])
app.include_router(audio.router, prefix="/api/audio", tags=["AUDIO TOOL"])
app.include_router(image.router, prefix="/api/image", tags=["IMAGE TOOL"])
app.include_router(ggdrive.router, prefix="/api/ggdrive", tags=["GOOGLE DRIVE TOOL"])
app.include_router(data.router, prefix="/api/data", tags=["DATA TOOL"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
