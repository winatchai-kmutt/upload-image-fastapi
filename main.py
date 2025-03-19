from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil

app = FastAPI()

UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ให้ FastAPI ให้บริการไฟล์ในโฟลเดอร์ "/tmp/uploads"
app.mount("/uploads", StaticFiles(directory="/tmp/uploads"), name="uploads")


@app.get("/")
async def root():
    return {"message": "Hello world from Vee"}


@app.post("/upload/")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    folder_name: str = Form(...)
):
    folder_path = UPLOAD_DIR / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    file_path = folder_path / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    base_url = str(request.base_url).rstrip('/')
    full_url = f"{base_url}/uploads/{folder_name}/{file.filename}"

    return {"image_url": full_url}


# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
