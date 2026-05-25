import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ResearchAgents:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

        self._summarizer_system = (
            "Summarize the retrieved research papers and present concise summaries to the user. "
            "JUST GIVE THE RELEVANT SUMMARIES OF THE RESEARCH PAPER AND NOT YOUR THOUGHT PROCESS."
        )
        self._analyzer_system = (
            "Analyze the summaries of the research papers and provide a list of advantages and "
            "disadvantages for each paper in a pointwise format. "
            "JUST GIVE THE ADVANTAGES AND DISADVANTAGES, NOT YOUR THOUGHT PROCESS."
        )

    def _call(self, system_msg: str, user_msg: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        return response.choices[0].message.content or ""

    def summarize_paper(self, paper_summary: str) -> str:
        """Generates a concise summary of the research paper."""
        return self._call(
            self._summarizer_system,
            f"Summarize this paper: {paper_summary}",
        )

    def analyze_advantages_disadvantages(self, summary: str) -> str:
        """Generates advantages and disadvantages of the research paper."""
        return self._call(
            self._analyzer_system,
            f"Provide advantages and disadvantages for this paper: {summary}",
        )
