import mimetypes
from docx import Document

def docx_to_text(file_path):
    # Validate MIME type
    file_type, _ = mimetypes.guess_type(file_path)
    expected_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if file_type != expected_type:
        raise ValueError(f"Not a valid Word document: detected type is '{file_type}'")

    # Extract text from the document
    doc = Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    print("the text is ----------->", text)
    return text