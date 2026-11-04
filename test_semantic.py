from app.parser import extract_text
from app.matching import semantic_similarity

resume_text = extract_text("resume.pdf")

jd_text = """
We are looking for a Python developer.
Candidate should understand SQL,
machine learning, and software development.
"""

score = semantic_similarity(resume_text, jd_text)

print("Semantic Similarity:", score, "%")
