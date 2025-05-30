import fitz
from fastapi import UploadFile
from .sanitizer import sanitize_text

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from a PDF or TXT file"""
    content = await file.read()
    
    if file.filename.endswith(".pdf"):
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        # Sanitize the extracted text
        return sanitize_text(text)
    elif file.filename.endswith(".txt"):
        text = content.decode("utf-8")
        # Sanitize the text file content
        return sanitize_text(text)
    else:
        raise ValueError("File must be a PDF or TXT file") 