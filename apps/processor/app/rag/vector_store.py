"""Workspace-partitioned vector store with hybrid dense-lexical similarity search."""

from __future__ import annotations
import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple
from app.schemas.workspace import DocumentChunk


def tokenize(text: str) -> List[str]:
    """Tokenize and lower-case text into alphanumeric words."""
    return [w.lower() for w in re.findall(r"\b[A-Za-z0-9\$\.\%\-\_]+\b", text)]


def compute_dense_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Generate a deterministic unit-normalized dense feature embedding.
    Uses multi-hash projection with term weights to produce consistent semantic coordinates.
    """
    tokens = tokenize(text)
    if not tokens:
        return [0.0] * dim

    vec = [0.0] * dim
    counts = Counter(tokens)

    for token, count in counts.items():
        # Compute term weight (log-scaled frequency)
        weight = 1.0 + math.log(count)
        # Primary hash and secondary hash
        h1 = abs(hash(token)) % dim
        h2 = abs(hash(token + "_salt")) % dim
        sign = 1.0 if (hash(token) % 2 == 0) else -1.0

        vec[h1] += weight * sign
        vec[h2] += 0.5 * weight * (-sign)

    # Unit normalization (L2 norm)
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]

    return vec


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute dot product of two unit-normalized vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))


class WorkspaceVectorStore:
    """Workspace-isolated index storing chunks, embeddings, and keyword indices."""

    def __init__(self):
        # workspace_id -> list of (DocumentChunk, embedding_vector)
        self._stores: Dict[str, List[Tuple[DocumentChunk, List[float]]]] = defaultdict(list)
        # workspace_id -> token -> set of chunk_ids
        self._inverted_indices: Dict[str, Dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))

    def add_chunks(self, workspace_id: str, chunks: List[DocumentChunk]) -> int:
        """Index a batch of chunks into the isolated workspace store."""
        added = 0
        for chunk in chunks:
            emb = compute_dense_embedding(chunk.text_content)
            self._stores[workspace_id].append((chunk, emb))

            # Inverted index for exact/lexical matches
            tokens = tokenize(chunk.text_content)
            for t in tokens:
                self._inverted_indices[workspace_id][t][chunk.chunk_id] += 1

            added += 1
        return added

    def search(
        self,
        workspace_id: str,
        query: str,
        top_k: int = 5,
        dense_weight: float = 0.65,
        lexical_weight: float = 0.35,
    ) -> List[DocumentChunk]:
        """
        Hybrid search combining dense cosine similarity and lexical keyword overlap.
        Guarantees strict workspace isolation.
        """
        store = self._stores.get(workspace_id, [])
        if not store:
            return []

        query_emb = compute_dense_embedding(query)
        query_tokens = set(tokenize(query))

        ranked: List[Tuple[float, DocumentChunk]] = []

        for chunk, chunk_emb in store:
            # 1. Dense Cosine Similarity
            dense_score = max(0.0, cosine_similarity(query_emb, chunk_emb))

            # 2. Lexical / Keyword Overlap
            chunk_tokens = tokenize(chunk.text_content)
            overlap = sum(1 for qt in query_tokens if qt in chunk_tokens)
            lexical_score = overlap / max(1, len(query_tokens))

            # Bonus for exact clause or document name match
            clause_bonus = 0.0
            if chunk.clause_reference:
                clause_tokens = set(tokenize(chunk.clause_reference))
                if query_tokens.intersection(clause_tokens):
                    clause_bonus = 0.15

            # Combined hybrid score
            hybrid_score = (dense_weight * dense_score) + (lexical_weight * lexical_score) + clause_bonus

            # Attach score to chunk copy
            scored_chunk = chunk.model_copy(update={"score": round(hybrid_score, 4)})
            ranked.append((hybrid_score, scored_chunk))

        # Sort descending by score
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in ranked[:top_k]]

    def get_chunk_count(self, workspace_id: str) -> int:
        return len(self._stores.get(workspace_id, []))

    def clear_workspace(self, workspace_id: str) -> None:
        self._stores.pop(workspace_id, None)
        self._inverted_indices.pop(workspace_id, None)


# Global Vector Store Singleton
VECTOR_STORE = WorkspaceVectorStore()

