"""Lightweight vector index for RAG over knowledge entries using TF-IDF."""

from __future__ import annotations

import math
import pickle
from collections import Counter
from pathlib import Path

from chainlens.models import KnowledgeEntry


class VectorIndex:
    """TF-IDF-based vector index for knowledge retrieval.

    No external service needed — pure Python with sklearn-like math.
    """

    def __init__(self, index_dir: str = ".cache/knowledge_index") -> None:
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._entries: list[KnowledgeEntry] = []
        self._vocab: dict[str, int] = {}
        self._tfidf_matrix: list[dict[int, float]] = []

    def rebuild(self, entries: list[KnowledgeEntry]) -> None:
        """Build TF-IDF index from scratch."""
        self._entries = entries
        if not entries:
            self._vocab = {}
            self._tfidf_matrix = []
            return

        docs = [self._tokenize(e.title + " " + e.summary) for e in entries]
        self._vocab = self._build_vocab(docs)
        self._tfidf_matrix = self._compute_tfidf(docs)

    def _tokenize(self, text: str) -> list[str]:
        import re
        tokens = re.findall(r"[a-z]+", text.lower())
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "about",
            "this", "that", "these", "those", "it", "its", "and", "but",
            "or", "nor", "not", "so", "yet", "if", "then", "else", "than",
            "also", "very", "just", "each", "all", "any", "both", "few", "more",  # noqa: E501
            "most", "other", "some", "such", "no", "only",
            "own", "same", "while", "how", "what", "which", "who", "whom",
            "when", "where", "why",
        }
        return [t for t in tokens if t not in stopwords and len(t) > 2]

    def _build_vocab(self, docs: list[list[str]]) -> dict[str, int]:
        vocab: dict[str, int] = {}
        for doc in docs:
            for token in doc:
                if token not in vocab:
                    vocab[token] = len(vocab)
        return vocab

    def _compute_tfidf(self, docs: list[list[str]]) -> list[dict[int, float]]:
        n_docs = len(docs)
        df: Counter = Counter()
        for doc in docs:
            for token in set(doc):
                if token in self._vocab:
                    df[token] += 1

        matrix: list[dict[int, float]] = []
        for doc in docs:
            tf = Counter(doc)
            vec: dict[int, float] = {}
            for token, count in tf.items():
                if token in self._vocab and df[token] > 0:
                    tfidf = (1 + math.log10(count)) * math.log10(n_docs / df[token])
                    vec[self._vocab[token]] = tfidf
            matrix.append(vec)
        return matrix

    def search(self, query: str, top_k: int = 5) -> list[KnowledgeEntry]:
        """Search entries by TF-IDF cosine similarity."""
        query_tokens = self._tokenize(query)
        if not query_tokens or not self._entries:
            return []

        q_vec: dict[int, float] = {}
        for token in query_tokens:
            if token in self._vocab:
                q_vec[self._vocab[token]] = q_vec.get(self._vocab[token], 0) + 1

        q_norm = math.sqrt(sum(v * v for v in q_vec.values()))
        if q_norm == 0:
            return []

        scores: list[tuple[int, float]] = []
        for i, doc_vec in enumerate(self._tfidf_matrix):
            dot = sum(q_vec.get(dim, 0) * val for dim, val in doc_vec.items())
            doc_norm = math.sqrt(sum(v * v for _, v in doc_vec.items()))
            if doc_norm > 0:
                sim = dot / (q_norm * doc_norm)
                scores.append((i, sim))

        scores.sort(key=lambda x: -x[1])
        return [self._entries[i] for i, _ in scores[:top_k] if scores[0][1] > 0]

    def add_entry(self, entry: KnowledgeEntry) -> None:
        """Add a single entry and rebuild index."""
        self._entries.append(entry)
        self.rebuild(self._entries)

    def save(self) -> None:
        state = {
            "entries": self._entries,
            "vocab": self._vocab,
        }
        path = self.index_dir / "index.pkl"
        with open(path, "wb") as f:
            pickle.dump(state, f)

    def load(self) -> bool:
        path = self.index_dir / "index.pkl"
        if not path.exists():
            return False
        with open(path, "rb") as f:
            state = pickle.load(f)
        self._entries = state["entries"]
        self._vocab = state["vocab"]
        self._tfidf_matrix = self._compute_tfidf(
            [self._tokenize(e.title + " " + e.summary) for e in self._entries]
        )
        return len(self._entries) > 0
