import re

from .skills import extract_skills
from .matching import semantic_similarity


ACTION = {
    "built",
    "developed",
    "designed",
    "implemented",
    "improved",
    "reduced",
    "deployed",
    "trained",
    "optimized",
    "led",
    "automated",
    "achieved"
}


CORE = [
    "education",
    "experience",
    "projects",
    "skills"
]


def impact_score(text):

    lines = [
        line.strip("-•* \t")
        for line in text.splitlines()
        if len(line.split()) > 4
    ]

    if not lines:
        return 0.0

    good = sum(
        1
        for line in lines
        if re.search(r"\d", line)
        or line.split()[0].lower() in ACTION
    )

    return good / len(lines)


def analyze(resume_text, sections, jd):

    resume_skills = extract_skills(resume_text)

    jd_skills = extract_skills(jd)

    matched = resume_skills & jd_skills

    missing = jd_skills - resume_skills

    skill_match = len(matched) / max(len(jd_skills), 1)

    semantic = semantic_similarity(
        resume_text,
        jd
    ) / 100

    structure = sum(
        bool(sections.get(section))
        for section in CORE
    ) / len(CORE)

    impact = impact_score(resume_text)

    total = 100 * (
        0.40 * skill_match
        + 0.25 * semantic
        + 0.20 * impact
        + 0.15 * structure
    )

    return {
        "total": round(total, 1),

        "breakdown": {
            "skill_match": round(skill_match, 2),
            "semantic": round(semantic, 2),
            "impact": round(impact, 2),
            "structure": round(structure, 2)
        },

        "matched_skills": sorted(matched),

        "missing_skills": sorted(missing),

        "missing_sections": [
            section
            for section in CORE
            if not sections.get(section)
        ]
    }