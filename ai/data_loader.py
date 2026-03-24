from pypdf import PdfReader
from docx import Document

def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def load_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_document(file_path):
    file_path = file_path.lower()

    if file_path.endswith(".txt"):
        return load_text(file_path)

    elif file_path.endswith(".pdf"):
        return load_pdf(file_path)

    elif file_path.endswith(".docx"):
        return load_docx(file_path)

    else:
        print(f"Unsupported file: {file_path}")
        return ""