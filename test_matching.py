from app.matching import match_skills


resume = """
Python
Java
SQL
Machine Learning
"""

job_description = """
Python
SQL
Django
Machine Learning
Git
"""

result = match_skills(resume, job_description)

print(result)