import requests

# Semantic Scholar Graph API — generous rate limits, no key required for basic use.
# Covers ArXiv, PubMed, ACL Anthology, IEEE and more in one endpoint.
_BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
_FIELDS = "title,abstract,url,year,authors,externalIds"
_HEADERS = {
    "User-Agent": "AI-Portfolio-Demo/1.0 (https://github.com/ashishk-yadav/AI-portfolio; educational use)"
}


class DataLoader:
    def __init__(self):
        pass

    def fetch_arxiv_papers(self, query: str, max_results: int = 5) -> list:
        """
        Fetches academic papers via the Semantic Scholar API.
        Returns ArXiv links when available; falls back to the Semantic Scholar URL.

        Returns list of dicts with keys — title, summary, link.
        Raises RuntimeError with a descriptive message on failure.
        """
        if not query or not query.strip():
            raise RuntimeError("Search query is empty. Enter a topic and try again.")

        params = {
            "query": query.strip(),
            "limit": max_results,
            "fields": _FIELDS,
        }

        try:
            resp = requests.get(_BASE_URL, params=params, headers=_HEADERS, timeout=15)
        except requests.exceptions.Timeout:
            raise RuntimeError("Semantic Scholar API timed out. Check your connection and try again.")
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Could not reach Semantic Scholar API: {e}")

        if resp.status_code == 429:
            raise RuntimeError(
                "Semantic Scholar is rate-limiting this IP (HTTP 429). "
                "Wait a minute and try again."
            )
        if not resp.ok:
            raise RuntimeError(
                f"Semantic Scholar API returned HTTP {resp.status_code}."
            )

        papers = []
        for p in resp.json().get("data", []):
            # Prefer the ArXiv link when the paper is on ArXiv
            arxiv_id = (p.get("externalIds") or {}).get("ArXiv")
            link = (
                f"https://arxiv.org/abs/{arxiv_id}"
                if arxiv_id
                else (p.get("url") or "")
            )
            papers.append({
                "title": p.get("title") or "Untitled",
                "summary": p.get("abstract") or "No abstract available.",
                "link": link,
            })

        return papers
