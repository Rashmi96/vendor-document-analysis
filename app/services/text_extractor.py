import pandas as pd
from docx import Document
from PIL import Image
import pytesseract
import fitz
import os
from PyPDF2 import PdfReader
from pathlib import Path
from app import Config

from app.utils.loggers import log_message

def extract():
    final_data = []
    for filename in os.listdir(Config.UPLOAD_FOLDER):
        try:
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            ext = Path(filename).suffix.lstrip('.')
            # extracted_data[filename] = extract_text(file_path)
            packet = create_data_packet(filename, ext, extract_text(file_path))
            final_data.append(packet)
            log_message(f"Extraction complete for {filename}")
        except Exception as e:
            return str(e)
    print(final_data)
    return final_data


def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_word(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_file(file_path)
    elif file_path.endswith('xlsx'):
        return extract_from_excel(file_path)
    elif file_path.endswith(('.png', '.jpg', '.jpeg')):
        return extract_image(file_path)
    return None


def create_data_packet(file_name, file_type, file_content):
    data_packet = {}
    data_packet["file_name"] = file_name
    data_packet["file_type"] = file_type
    data_packet["content"] = file_content
    return data_packet


def extract_pdf(file_path, text=None):
    try:
        is_text_extracted = False
        reader = PdfReader(file_path)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                is_text_extracted = True
        if is_text_extracted:
            return text
        else:
            print(f"No text found with PdfReader, using fitz for {file_path}")
            doc = fitz.open(file_path)
            for i in range(doc.page_count):
                page = doc.load_page(i)
                text = page.get_text("text")  # Extract text
                if text.strip():  # Ensure non-empty text
                    return text
                else:
                    # If page is still non-text, render page as image (optional)
                    pix = page.get_pixmap()
                    base_name, ext = os.path.splitext(file_path)
                    pix.save(f"page-{i + 1}-{base_name}.png")
                    print(f"Page {i + 1} rendered as image.")
    except Exception as e:
        return f"Error reading Excel file: {str(e)}"


def extract_from_excel(file_path):
    try:
        log_message(f"Inside XLSX extraction method")
        excel_data = pd.ExcelFile(file_path)
        all_data = {}
        for sheet_name in excel_data.sheet_names:
            df = pd.read_excel(excel_data, sheet_name=sheet_name)
            all_data[sheet_name] = df.to_dict()
        return all_data
    except Exception as e:
        return f"Error reading Excel file: {str(e)}"


def extract_word(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def extract_text_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
    return text


def extract_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text
