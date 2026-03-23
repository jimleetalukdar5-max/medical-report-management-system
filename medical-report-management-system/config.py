import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER =  "uploads"

    AES_KEY_B64 = os.getenv("AES_KEY_B64")
    SECRET_KEY = os.getenv("SECRET_KEY")

    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 10))