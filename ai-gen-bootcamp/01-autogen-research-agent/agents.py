import os
from llm_provider import get_llm_response

class ResearchAgents:
    """
    Provider-agnostic research agents.
    Reads LLM_PROVIDER / LLM_API_KEY / LLM_MODEL from env vars set by llm_provider.provider_sidebar().
    """

    _summarizer_system = (
        "Summarize the retrieved research papers and present concise summaries to the user. "
        "JUST GIVE THE RELEVANT SUMMARIES OF THE RESEARCH PAPER AND NOT YOUR THOUGHT PROCESS."
    )
    _analyzer_system = (
        "Analyze the summaries of the research papers and provide a list of advantages and "
        "disadvantages for each paper in a pointwise format. "
        "JUST GIVE THE ADVANTAGES AND DISADVANTAGES, NOT YOUR THOUGHT PROCESS."
    )

    def summarize_paper(self, paper_summary: str) -> str:
        """Generates a concise summary of the research paper."""
        return get_llm_response(
            messages=[
                {"role": "system", "content": self._summarizer_system},
                {"role": "user", "content": f"Summarize this paper: {paper_summary}"},
            ]
        )

    def analyze_advantages_disadvantages(self, summary: str) -> str:
        """Generates advantages and disadvantages of the research paper."""
        return get_llm_response(
            messages=[
                {"role": "system", "content": self._analyzer_system},
                {"role": "user", "content": f"Provide advantages and disadvantages for this paper: {summary}"},
            ]
        )
