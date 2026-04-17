"""
etape1_pdf.py - Extraction du texte brut depuis PDF, TXT, HTML, DOCX
TP5 : support multi-format
"""
import os
import re


def extract_text_raw(filepath):
    """Retourne le texte brut d'un fichier selon son extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext == ".txt":
        return _extract_txt(filepath)
    elif ext in (".html", ".htm"):
        return _extract_html(filepath)
    elif ext == ".docx":
        return _extract_docx(filepath)
    else:
        return ""


def extract_words(filepath):
    """Retourne la liste de mots extraits d'un fichier."""
    text = extract_text_raw(filepath)
    text = text.lower()
    mots = re.findall(r"[a-zA-ZÀ-ÿ]{2,}", text)
    return mots


# ── Extracteurs par format ─────────────────────────────────────── #

def _extract_pdf(filepath):
    try:
        import PyPDF2
        text = ""
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        return text
    except Exception:
        pass
    try:
        from pdfminer.high_level import extract_text
        return extract_text(filepath) or ""
    except Exception:
        return ""


def _extract_txt(filepath):
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


def _extract_html(filepath):
    try:
        from html.parser import HTMLParser

        class _Strip(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts = []
                self._skip = False

            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style"):
                    self._skip = True

            def handle_endtag(self, tag):
                if tag in ("script", "style"):
                    self._skip = False

            def handle_data(self, data):
                if not self._skip:
                    self.parts.append(data)

        content = _extract_txt(filepath)
        parser = _Strip()
        parser.feed(content)
        return " ".join(parser.parts)
    except Exception:
        return ""


def _extract_docx(filepath):
    try:
        import docx
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""
