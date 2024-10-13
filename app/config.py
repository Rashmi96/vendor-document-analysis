import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = 'static/uploads'
    DOWNLOAD_FOLDER = os.path.abspath('static/reports')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'xlsx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size: 16MB
