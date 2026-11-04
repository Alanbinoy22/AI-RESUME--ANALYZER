import json
import re
with open("data/skills.json", "r") as file:

    SKILLS = json.load(file)
    ALIASES = {

    "sklearn": "scikit-learn",

    "js": "javascript",

    "ml": "machine learning",

    "dl": "deep learning",

    "nlp": "natural language processing",

    "k8s": "kubernetes"

}
    
def _has(term, text):

    pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"

    return re.search(pattern, text) is not None
def extract_skills(text):

    text = text.lower()

    found = {

        skill for skill in SKILLS

        if _has(skill, text)

    }

    found |= {

        full for alias, full in ALIASES.items()

        if _has(alias, text)

    }

    return found