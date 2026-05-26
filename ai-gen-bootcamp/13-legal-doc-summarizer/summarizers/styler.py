import os
from dotenv import load_dotenv
from llm_provider import get_llm_response

load_dotenv()

STYLE_INSTRUCTIONS = {
    "Executive brief": "Rewrite as an executive brief with 5-7 crisp bullets, each starting with a strong verb. Avoid jargon.",
    "Meeting minutes": "Rewrite as meeting minutes with sections: Attendees, Agenda, Decisions, Action Items.",
    "Legal (Obligations/Risks/Next steps)": "Rewrite as a legal-style summary with three headings: Obligations, Risks, Next Steps. Use numbered bullets.",
    "Research abstract": "Rewrite as an academic abstract with Background, Method, Results, and Conclusion in 120-180 words.",
    "PR/FAQ": "Rewrite as PR/FAQ: first a press-release style paragraph, then 5-8 FAQs with concise answers.",
    "SWOT": "Rewrite as a SWOT analysis with 3-5 bullets each under Strengths, Weaknesses, Opportunities, Threats.",
}


def style_summary(summary: str, style: str) -> str:
    instr = STYLE_INSTRUCTIONS.get(style, "Rewrite clearly.")
    prompt = f"{instr}\n\nText to rewrite:\n{summary}"
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You transform a given summary into different business-friendly formats."},
            {"role": "user", "content": prompt},
        ]
    ).strip()


def focus_summary(summary: str, query: str) -> str:
    if not (query and query.strip()):
        return summary
    prompt = (
        f"Refocus the following summary so it answers the question '{query}'. "
        f"Remove irrelevant points, keep concise bullets.\n\nSummary:\n{summary}"
    )
    return get_llm_response(
        messages=[
            {"role": "system", "content": "You refine summaries to focus on answering a specific question."},
            {"role": "user", "content": prompt},
        ]
    ).strip()
