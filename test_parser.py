from app.parser import extract_text


resume_path = "resume.pdf"

text = extract_text(resume_path)

print(text)