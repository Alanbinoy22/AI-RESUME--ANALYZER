from app.parser import extract_text

from app.sections import split_sections


resume_text = extract_text("resume.pdf")

sections = split_sections(resume_text)

print(sections)