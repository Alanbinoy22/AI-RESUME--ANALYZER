
import shutil
import tempfile
import os

from fastapi import FastAPI, UploadFile, File, Form

from .parser import extract_text
from .sections import split_sections
from .scoring import analyze


app = FastAPI(title="AI Resume Analyzer")


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...)
):

    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    ) as file:

        shutil.copyfileobj(resume.file, file)

        file.flush()

        temp_path = file.name

    # Extract text and delete temporary PDF
    try:

        text = extract_text(temp_path)

    finally:

        os.remove(temp_path)

    # Check whether PDF text was extracted
    if len(text) < 200:

        return {
            "error": "Could not read text. Is this a scanned PDF?"
        }

    # Split resume into sections
    sections = split_sections(text)

    # Analyze resume against job description
    result = analyze(
        text,
        sections,
        jd
    )

    # Return analysis result
    return result
