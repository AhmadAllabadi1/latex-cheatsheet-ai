import os
from dotenv import load_dotenv


load_dotenv()

import fitz
from fastapi.responses import FileResponse, JSONResponse
from fastapi import FastAPI, UploadFile, File, Form
from utils.latex_gen import render_latex
from utils.compile_latex import compile_latex_to_pdf
from utils.ai_engine import generate_cheatsheet


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is working!"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    font_size: str = Form("\\small"),
    columns: int = Form(2),
    orientation: str = Form("portrait")
):
    if file.filename.endswith(".pdf"):
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
    elif file.filename.endswith(".txt"):
        content = await file.read()
        text = content.decode("utf-8")
    else:
        return JSONResponse(status_code=500, content={"error": "File must be a PDF or TXT file"})
    
    ai_generated_text = generate_cheatsheet(text)
    latex_content = render_latex(ai_generated_text, font_size, columns, orientation)
    latex_pdf = compile_latex_to_pdf(latex_content)
    #return {"latex_content": latex_content}
    return FileResponse(path=latex_pdf, media_type="application/pdf", filename="cheatsheet.pdf")
