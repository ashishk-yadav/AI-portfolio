import io
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup

def load_file(uploaded):
    if uploaded.type == "application/pdf":
        reader = PdfReader(uploaded)
        text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
    else:
        text = uploaded.read().decode("utf-8")
    return text


def load_from_url(url: str, timeout: int = 20, max_bytes: int = 20*1024*1024):
    """Download content from URL and extract text + metadata.
    Returns: (text, meta_dict)
      meta: {type: 'pdf'|'html'|'binary'|'text', size_bytes: int, pages?: int, title?: str, content_type?: str}
    """
    if not url or not isinstance(url, str):
        raise ValueError("Please provide a valid URL.")
    r = requests.get(url, stream=True, timeout=timeout)
    r.raise_for_status()
    ctype = (r.headers.get("Content-Type") or "").lower()
    size = 0
    buf = io.BytesIO()
    for chunk in r.iter_content(8192):
        if not chunk:
            continue
        buf.write(chunk)
        size += len(chunk)
        if size > max_bytes:
            break
    buf.seek(0)

    meta = {"size_bytes": size, "content_type": ctype}

    # Heuristic: if content type says PDF or URL endswith .pdf -> treat as PDF
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        reader = PdfReader(buf)
        text = " ".join([p.extract_text() or "" for p in reader.pages])
        meta.update({"type": "pdf", "pages": len(reader.pages)})
        return text.strip(), meta

    # Else try to read as HTML
    try:
        raw = buf.getvalue()
        # Use response encoding if present, else fall back to utf-8
        enc = r.encoding or "utf-8"
        html = raw.decode(enc, errors="ignore")
        soup = BeautifulSoup(html, "html.parser")
        # Remove script/style
        for s in soup(["script", "style", "noscript"]):
            s.extract()
        title = (soup.title.string.strip() if soup.title and soup.title.string else "")
        text = " ".join(soup.get_text(separator=" ").split())
        meta.update({"type": "html", "title": title})
        return text.strip(), meta
    except Exception:
        # Fallback: treat as plain text
        try:
            text = buf.getvalue().decode("utf-8", errors="ignore")
            meta.update({"type": "text"})
            return text.strip(), meta
        except Exception:
            meta.update({"type": "binary"})
            return "", meta
