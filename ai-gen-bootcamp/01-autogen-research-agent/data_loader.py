import time
import requests
import xml.etree.ElementTree as ET

# ArXiv's API guidelines ask callers to identify themselves via User-Agent
# and to stay below 3 req/s. A polite header avoids 429 rate-limit responses.
_HEADERS = {
    "User-Agent": "AI-Portfolio-Demo/1.0 (https://github.com/ashishk-yadav/AI-portfolio; educational use)"
}


class DataLoader:
    def __init__(self):
        pass

    def fetch_arxiv_papers(self, query: str, max_results: int = 5) -> list:
        """
        Fetches research papers from the ArXiv API.

        Returns list of dicts with keys — title, summary, link.
        Raises RuntimeError with a descriptive message on failure.
        """
        if not query or not query.strip():
            raise RuntimeError("Search query is empty. Enter a topic and try again.")

        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query=all:{requests.utils.quote(query.strip())}"
            f"&start=0&max_results={max_results}"
        )

        # Retry once on 429 with a short back-off
        for attempt in (1, 2):
            try:
                response = requests.get(url, headers=_HEADERS, timeout=15)
            except requests.exceptions.Timeout:
                raise RuntimeError(
                    "ArXiv API timed out (15 s). Check your internet connection and try again."
                )
            except requests.exceptions.ConnectionError as e:
                raise RuntimeError(f"Could not reach ArXiv API: {e}")

            if response.status_code == 429:
                if attempt == 1:
                    # ArXiv rate-limit — wait and retry once
                    time.sleep(5)
                    continue
                raise RuntimeError(
                    "ArXiv is rate-limiting this IP (429). Wait a minute and search again."
                )

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise RuntimeError(f"ArXiv API returned an error: {e}")

            break  # success — exit retry loop

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            raise RuntimeError(
                f"Could not parse ArXiv response (status {response.status_code}): {e}"
            )

        return [
            {
                "title": (entry.find("{http://www.w3.org/2005/Atom}title").text or "").strip(),
                "summary": (entry.find("{http://www.w3.org/2005/Atom}summary").text or "").strip(),
                "link": (entry.find("{http://www.w3.org/2005/Atom}id").text or "").strip(),
            }
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry")
        ]
