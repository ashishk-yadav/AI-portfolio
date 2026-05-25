# utils/metrics.py
import re
import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer

def _tfidf_matrix(texts: List[str]):
    vect = TfidfVectorizer().fit_transform(texts)
    return vect

def _cosine(A, B):
    return (A @ B.T).toarray()

def coverage(summary: str, chunks: List[str]) -> float:
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', summary) if s.strip()]
    if not sents or not chunks:
        return 0.0
    tfidf = _tfidf_matrix(sents + chunks)
    S = tfidf[:len(sents)]
    C = tfidf[len(sents):]
    sims = _cosine(S, C)
    return float(np.mean(np.max(sims, axis=1)))  # avg best match per sentence

def redundancy(summary: str) -> float:
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', summary) if s.strip()]
    if len(sents) < 2:
        return 0.0
    tfidf = _tfidf_matrix(sents)
    sims = _cosine(tfidf, tfidf)
    # take upper triangle without diagonal
    iu = np.triu_indices_from(sims, k=1)
    if len(iu[0]) == 0:
        return 0.0
    return float(np.mean(sims[iu]))

def sentence_citations(summary: str, chunks: List[str]):
    """Return list of (sentence, best_chunk_index, best_score)."""
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', summary) if s.strip()]
    if not sents or not chunks:
        return []
    tfidf = _tfidf_matrix(sents + chunks)
    S = tfidf[:len(sents)]
    C = tfidf[len(sents):]
    sims = _cosine(S, C)
    out = []
    for i, row in enumerate(sims):
        j = int(np.argmax(row))
        out.append((sents[i], j, float(row[j])))
    return out
