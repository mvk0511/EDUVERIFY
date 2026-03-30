from pdfminer.high_level import extract_text as pdf_extract

def extract_text(file_path):
    try:
        return pdf_extract(file_path) or ""
    except Exception:
        return ""
