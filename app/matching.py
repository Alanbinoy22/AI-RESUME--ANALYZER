from app.skills import extract_skills


def match_skills(resume_text, jd_text):

    resume_skills = extract_skills(resume_text)

    jd_skills = extract_skills(jd_text)

    matched = resume_skills & jd_skills

    missing = jd_skills - resume_skills

    skill_match = len(matched) / max(len(jd_skills), 1)

    return {

        "skill_match": round(skill_match * 100, 2),

        "matched_skills": sorted(matched),

        "missing_skills": sorted(missing)

    }
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_similarity(resume_text, jd_text):

    embeddings = model.encode(
        [resume_text, jd_text],
        convert_to_tensor=True
    )

    similarity = util.cos_sim(
        embeddings[0],
        embeddings[1]
    )

    score = float(similarity.item())

    return round(score * 100, 2)    