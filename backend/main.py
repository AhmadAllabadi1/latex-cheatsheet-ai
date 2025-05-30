import os
from dotenv import load_dotenv
import tempfile
from typing import List
from fastapi import Form, File, UploadFile
import asyncio
import shutil
from pathlib import Path


load_dotenv()

from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI
from utils.latex_gen import render_latex
from utils.compile_latex import compile_latex_to_pdf
from utils.text_extractor import extract_text_from_file
from utils.chunker import chunk_text, count_tokens
from utils.async_summarizer import summarize_all_chunks
from fastapi.middleware.cors import CORSMiddleware

# Create a directory for storing PDFs
PDF_STORAGE_DIR = Path("pdf_storage")
PDF_STORAGE_DIR.mkdir(exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Backend is working!"}

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    font_size: str = Form(...),
    columns: int = Form(...),
    orientation: str = Form(...)
):
    try:
        # Extract text from all files
        all_text = ""
        for file in files:
            try:
                text = await extract_text_from_file(file)
                all_text += text + "\n\n"  # Add spacing between files
            except ValueError as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Error processing {file.filename}: {str(e)}"}
                )
        
        # Count total tokens
        total_tokens = count_tokens(all_text)
        
        # If text is too long, chunk it
        if total_tokens > 4000:  # Adjust this threshold as needed
            text_chunks = chunk_text(all_text, max_tokens=4000, overlap_tokens=200)
            processed_chunks = await summarize_all_chunks(text_chunks)
            ai_generated_text = "\n".join(processed_chunks)
        else:
            # Process the entire text at once
            processed_chunks = await summarize_all_chunks([all_text])
            ai_generated_text = processed_chunks[0]
        
        # Generate LaTeX and compile to PDF
        latex_content = render_latex(ai_generated_text, "\\" + font_size, columns, orientation)
        temp_pdf = compile_latex_to_pdf(latex_content)
        
        # Generate a unique filename
        pdf_filename = f"cheatsheet_{os.urandom(8).hex()}.pdf"
        pdf_path = PDF_STORAGE_DIR / pdf_filename
        
        # Copy the PDF to our storage directory
        shutil.copy2(temp_pdf, pdf_path)
        
        # Return both PDF and LaTeX content
        return JSONResponse(
            content={
                "pdf_url": f"/download/{pdf_filename}",
                "latex_code": latex_content
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}"}
        )

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = PDF_STORAGE_DIR / filename
    if not file_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "PDF file not found"}
        )
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename="cheatsheet.pdf"
    )

