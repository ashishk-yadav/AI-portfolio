import re
import numpy as np
import networkx as nx
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from .chunking import token_chunks

def _split_sentences(text: str) -> List[str]:
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sents if len(s.split()) > 5]

def _rank_sentences_textrank(sentences: List[str]) -> List[int]:
    vect = TfidfVectorizer().fit_transform(sentences)
    sim = (vect * vect.T).A
    np.fill_diagonal(sim, 0.0)
    G = nx.from_numpy_array(sim)
    scores = nx.pagerank(G)
    order = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)
    return order

def _rank_by_query(sentences: List[str], query: str) -> List[int]:
    vect = TfidfVectorizer().fit_transform(sentences + [query])
    S = vect[:-1]
    q = vect[-1]
    sims = (S @ q.T).toarray().ravel()
    order = list(np.argsort(-sims))
    return order

def quote_preserving(text: str, query: str = None, target_sents: int = 7) -> List[Tuple[str, int, float]]:
    """Return list of (sentence, best_chunk_index, score)."""
    sentences = _split_sentences(text[:50000])
    if not sentences:
        return []
    if query and query.strip():
        ranked = _rank_by_query(sentences, query.strip())
    else:
        ranked = _rank_sentences_textrank(sentences)

    chosen_idx = sorted(sorted(ranked[:target_sents]))  # keep original order
    chosen = [sentences[i] for i in chosen_idx]

    # Cite best chunk for each chosen sentence
    chunks = token_chunks(text, words_per_chunk=400, overlap=120)
    if not chunks:
        return [(s, -1, 0.0) for s in chosen]
    vect = TfidfVectorizer().fit_transform(chosen + chunks)
    S = vect[:len(chosen)]
    C = vect[len(chosen):]
    sims = (S @ C.T).toarray()
    out = []
    for i, row in enumerate(sims):
        j = int(np.argmax(row)); score = float(row[j])
        out.append((chosen[i], j, score))
    return out
