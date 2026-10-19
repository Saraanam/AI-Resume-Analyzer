
import pymupdf


def extract_text_from_pdf(file):
    text = ""

    # Open the uploaded PDF directly from memory
    with pymupdf.open(
        stream=file.getvalue(),
        filetype="pdf"
    ) as pdf:
        for page in pdf:
            text += page.get_text()

    return text
