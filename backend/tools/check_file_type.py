from pathlib import Path


def check_file_type(file_path):
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return "pdf"
        elif ext in [".html", ".htm"]:
            return "html"
        elif ext == [".docx", ".doc"]:
            return "doc"
        else:
            return ext[1:] 