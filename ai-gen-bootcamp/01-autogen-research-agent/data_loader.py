import json
import unicodedata
import requests

# OpenAlex — NSF-funded open academic graph, no API key required.
# Adding `mailto` places us in the "polite pool" (higher rate limits, no IP blocks).
_BASE_URL = "https://api.openalex.org/works"
_MAILTO = "ashishk.yadavai@gmail.com"
_HEADERS = {
    "User-Agent": "AI-Portfolio-Demo/1.0 (mailto:ashishk.yadavai@gmail.com)"
}


def _safe_str(text) -> str:
    """Normalize Unicode to clean UTF-8, dropping surrogates and invalid bytes.

    OpenAlex papers often contain Greek letters (α, β), math symbols, and
    accented characters that trigger 'ascii' codec errors in some LLM SDK
    versions. NFC normalization + a UTF-8 round-trip cleanly handles all of
    these without stripping meaningful content.
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFC", text)
    return text.encode("utf-8", errors="replace").decode("utf-8")


def _reconstruct_abstract(inverted_index: dict) -> str:
    """OpenAlex stores abstracts as word→[positions] dicts. Reconstruct plain text."""
    if not inverted_index:
        return "No abstract available."
    words = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words.append((pos, word))
    return " ".join(w for _, w in sorted(words))


class DataLoader:
    def __init__(self):
        pass

    def fetch_arxiv_papers(self, query: str, max_results: int = 5) -> list:
        """
        Fetches academic papers via the OpenAlex API.
        Returns ArXiv links when the paper is indexed on ArXiv; falls back to DOI/URL.

        Returns list of dicts with keys — title, summary, link.
        Raises RuntimeError with a descriptive message on failure.
        """
        if not query or not query.strip():
            raise RuntimeError("Search query is empty. Enter a topic and try again.")

        params = {
            "search": query.strip(),
            "per-page": max_results,
            "select": "title,abstract_inverted_index,ids,doi,primary_location,open_access",
            "mailto": _MAILTO,
        }

        try:
            resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=15)
        except requests.exceptions.Timeout:
            raise RuntimeError("OpenAlex API timed out. Check your connection and try again.")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Could not reach OpenAlex API: {e}")

        if resp.status_code == 429:
            raise RuntimeError("OpenAlex is rate-limiting this IP. Wait a moment and try again.")
        if not resp.ok:
            raise RuntimeError(f"OpenAlex API returned HTTP {resp.status_code}.")

        # Decode with explicit UTF-8 to handle non-ASCII chars before they hit
        # any codec boundary in the LLM SDK (some versions use ASCII internally).
        try:
            data = json.loads(resp.content.decode("utf-8", errors="replace"))
        except json.JSONDecodeError as e:
            raise RuntimeError(f"OpenAlex returned invalid JSON: {e}")

        papers = []
        for p in data.get("results", []):
            # Prefer ArXiv link → open-access URL → landing page → DOI
            ids = p.get("ids") or {}
            arxiv_url = ids.get("arxiv", "")
            oa_url = (p.get("open_access") or {}).get("oa_url", "")
            landing = ((p.get("primary_location") or {}).get("landing_page_url") or "")
            doi = p.get("doi") or ""
            link = arxiv_url or oa_url or landing or doi

            papers.append({
                "title": _safe_str(p.get("title") or "Untitled"),
                "summary": _safe_str(_reconstruct_abstract(p.get("abstract_inverted_index"))),
                "link": _safe_str(link),
            })

        return papers
