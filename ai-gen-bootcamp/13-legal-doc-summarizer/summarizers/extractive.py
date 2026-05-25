# summarizers/extractive.py
import re, math
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer

def _split_sentences(text: str):
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sents if len(s.split()) > 3]

def summarize(text: str, max_sents: int = 7):
    """Simple extractive TextRank-like baseline using TF-IDF cosine graph."""
    text = text[:30000]  # keep it snappy
    sents = _split_sentences(text)
    if not sents:
        return ""
    if len(sents) <= max_sents:
        return " ".join(sents)

    vect = TfidfVectorizer().fit_transform(sents)
    sim = (vect * vect.T).toarray()
    np.fill_diagonal(sim, 0.0)
    G = nx.from_numpy_array(sim)
    scores = nx.pagerank(G)
    top_idx = sorted(range(len(sents)), key=lambda i: scores[i], reverse=True)[:max_sents]
    top_idx.sort()  # keep original order
    return " ".join(sents[i] for i in top_idx)
