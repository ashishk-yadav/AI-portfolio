import arxiv


class DataLoader:
    def __init__(self):
        # num_retries=1: don't hammer the API repeatedly on rate-limit (429).
        # delay_seconds=3: polite pause between multi-page fetches.
        self._client = arxiv.Client(
            page_size=10,
            delay_seconds=3.0,
            num_retries=1,
        )

    def fetch_arxiv_papers(self, query: str, max_results: int = 5) -> list:
        """
        Fetches research papers from ArXiv using the official arxiv library.
        Returns list of dicts with keys — title, summary, link.
        Raises RuntimeError with a descriptive message on failure.
        """
        if not query or not query.strip():
            raise RuntimeError("Search query is empty. Enter a topic and try again.")

        search = arxiv.Search(
            query=query.strip(),
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        try:
            results = list(self._client.results(search))
        except arxiv.HTTPError as e:
            if e.status == 429:
                raise RuntimeError(
                    "ArXiv is temporarily rate-limiting this IP (HTTP 429). "
                    "Wait 1–2 minutes and try again — this clears on its own."
                )
            raise RuntimeError(f"ArXiv API error (HTTP {e.status}): {e}")
        except Exception as e:
            raise RuntimeError(f"ArXiv fetch failed: {e}")

        return [
            {
                "title": r.title,
                "summary": r.summary,
                "link": r.entry_id,
            }
            for r in results
        ]
