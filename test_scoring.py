from app.parser import extract_text

from app.sections import split_sections

from app.scoring import analyze


resume_text = extract_text("resume.pdf")

sections = split_sections(resume_text)


jd = """
We are looking for a Python developer.

Required skills:
Python, SQL, Django, Machine Learning, Git.

The candidate should have experience
in software development and projects.
"""


result = analyze(
    resume_text,
    sections,
    jd
)


print("\n===== RESUME ANALYSIS =====")

print("Overall Score:", result["total"], "/ 100")

print("\nScore Breakdown:")

for component, score in result["breakdown"].items():

    print(component, ":", score)


print("\nMatched Skills:")

print(result["matched_skills"])


print("\nMissing Skills:")

print(result["missing_skills"])


print("\nMissing Sections:")

print(result["missing_sections"])