
import cloudinary
import cloudinary.uploader
import os
import json
import firebase_admin
from dotenv import load_dotenv

from firebase_admin import credentials, auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header

# โหลด Environment Variables
load_dotenv()

# ตั้งค่า Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# เริ่มต้น Firebase Admin SDK (ต้องใช้ Firebase Service Account JSON)
firebase_creds = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_creds)
firebase_admin.initialize_app(cred)

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

# ✅ ฟังก์ชันตรวจสอบ Firebase Token


async def verify_firebase_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "")  # ดึง JWT Token ออกมา
    try:
        decoded_token = auth.verify_id_token(token)  # ตรวจสอบ JWT กับ Firebase
        return decoded_token  # คืนข้อมูลผู้ใช้ที่ยืนยันแล้ว
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.get("/")
async def root():
    return {"message": "Hello world from Vee"}

# ✅ API อัปโหลดรูปภาพ (ต้องใช้ JWT)


@app.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    folder_name: str = Form(...),
    user=Depends(verify_firebase_token)  # ⬅️ ตรวจสอบ JWT ก่อนอัปโหลด
):
    try:
        # อัปโหลดรูปไปที่ Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file, folder=folder_name, resource_type="image"
        )

        image_url = upload_result.get("secure_url")

        return {"image_url": image_url, "uploaded_by": user["uid"]}

    except Exception as e:
        return {"error": str(e)}


# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
