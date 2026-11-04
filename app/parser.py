import pdfplumber


def extract_text(path):

    with pdfplumber.open(path) as pdf:

        pages = []

        for page in pdf.pages:

            text = page.extract_text()

            if text:

                pages.append(text)

    return "\n".join(pages)