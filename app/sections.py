SECTION_HEADERS = {

    "education": [
        "education",
        "academic"
    ],

    "experience": [
        "experience",
        "internship",
        "work history"
    ],

    "projects": [
        "projects",
        "project work"
    ],

    "skills": [
        "skills",
        "technical skills"
    ],

    "certifications": [
        "certification",
        "courses"
    ]

}
def split_sections(text):

    sections = {"header": []}

    current = "header"

    for line in text.splitlines():

        low = line.strip().lower()

        hit = next(
            (
                k for k, words in SECTION_HEADERS.items()
                if len(low) < 30
                and any(low.startswith(w) for w in words)
            ),
            None
        )

        if hit:

            current = hit

            sections.setdefault(current, [])

        else:

            sections.setdefault(current, []).append(line)

    return {
        k: "\n".join(v).strip()
        for k, v in sections.items()
    }