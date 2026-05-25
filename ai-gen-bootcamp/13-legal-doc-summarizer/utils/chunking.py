# utils/chunking.py
from typing import List

def token_chunks(text: str, words_per_chunk: int = 400, overlap: int = 100) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    i = 0
    n = len(words)
    while i < n:
        j = min(i + words_per_chunk, n)
        chunk = " ".join(words[i:j])
        chunks.append(chunk)
        if j == n:
            break
        i = max(j - overlap, i + 1)
    return chunks
