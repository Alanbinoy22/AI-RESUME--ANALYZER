from app.parser import extract_text

from app.skills import extract_skills


resume_text = extract_text("resume.pdf")

skills = extract_skills(resume_text)

print("Detected Skills:")

for skill in sorted(skills):

    print(skill)