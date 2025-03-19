from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

# โหลด Environment Variables จากไฟล์ .env
load_dotenv()

# ตั้งค่า Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

app = FastAPI()

origins = [
    "https://socialapp-cablocfirebase.web.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello world from Vee"}


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), folder_name: str = Form(...)):
    try:
        # อัปโหลดรูปภาพไปยัง Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file, folder=folder_name, resource_type="image"
        )

        # ดึง URL ของภาพที่อัปโหลดแล้ว
        image_url = upload_result.get("secure_url")

        return {"image_url": image_url}

    except Exception as e:
        return {"error": str(e)}


# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
