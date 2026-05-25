import requests
import xml.etree.ElementTree as ET

class DataLoader:
    def __init__(self):
        pass

    def fetch_arxiv_papers(self, query: str, max_results: int = 5) -> list:
        """
        Fetches research papers from the ArXiv API.

        Returns:
            list: dicts with keys — title, summary, link.
        """
        url = (
            "http://export.arxiv.org/api/query"
            f"?search_query=all:{requests.utils.quote(query)}"
            f"&start=0&max_results={max_results}"
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.text)
            return [
                {
                    "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
                    "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text,
                    "link": entry.find("{http://www.w3.org/2005/Atom}id").text,
                }
                for entry in root.findall("{http://www.w3.org/2005/Atom}entry")
            ]
        except Exception:
            return []
