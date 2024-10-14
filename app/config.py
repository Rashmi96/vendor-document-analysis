import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = 'static/uploads'
    DOWNLOAD_FOLDER = os.path.abspath('static/reports')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'xlsx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max file size: 16MB
    CHUNK_SIZE = 5000
    PROMPT_QUESTION = os.path.abspath('static/prompt/prompt_question.json')
    TOKEN_LIMIT = 4000
    MAX_TOKENS_PER_REQUEST = 1000

