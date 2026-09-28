"""
Resume Parsing Module — supports PDF, DOCX, TXT via PyPDF2, python-docx, Apache Tika.
"""
import os
import re


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyPDF2."""
    try:
        import PyPDF2
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return _tika_fallback(file_path)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        return "\n".join(paragraphs)
    except Exception:
        return _tika_fallback(file_path)


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from plain TXT file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return ""


def _tika_fallback(file_path: str) -> str:
    """Fallback: use Apache Tika for extraction."""
    try:
        from tika import parser as tika_parser
        parsed = tika_parser.from_file(file_path)
        return (parsed.get("content") or "").strip()
    except Exception:
        return ""


def parse_resume_file(file_path: str) -> str:
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        text = extract_text_from_docx(file_path)
    elif ext == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        text = _tika_fallback(file_path)

    if not text:
        text = _tika_fallback(file_path)
    return text


def parse_resume_bytes(file_bytes: bytes, filename: str) -> str:
    """Parse resume from in-memory bytes (for Django file uploads)."""
    import tempfile
    ext = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        return parse_resume_file(tmp_path)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
