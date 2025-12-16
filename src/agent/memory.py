"""Lightweight in-memory components backing the planner and RAG stack."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence


@dataclass
class InMemoryStore:
    """Minimal memory store for retrieved exemplars and documents."""

    documents: List[str] = field(default_factory=list)

    def add(self, docs: Iterable[str]) -> None:
        self.documents.extend(docs)

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        # Naive substring relevance: prefer docs containing tokens from the query.
        terms = set(query.lower().split())
        scored: List[tuple[int, str]] = []
        for doc in self.documents:
            doc_terms = set(doc.lower().split())
            score = len(terms.intersection(doc_terms))
            scored.append((score, doc))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [doc for score, doc in scored[:k] if score > 0] or self.documents[:k]


@dataclass
class SimpleRetriever:
    """Retriever wrapper that uses InMemoryStore but exposes a stable interface."""

    store: InMemoryStore

    def embed_and_search(self, query: str, k: int = 5) -> List[str]:
        return self.store.retrieve(query, k)

    def add_documents(self, documents: Iterable[str]) -> None:
        self.store.add(documents)


@dataclass
class EchoGenerator:
    """Generator placeholder that returns a constrained echo of the prompt + citations."""

    max_chars: int = 1200

    def generate(self, prompt: str, context: Sequence[str]) -> str:
        citations = "\n".join(f"- context[{idx}]" for idx, _ in enumerate(context))
        trimmed = (prompt[: self.max_chars] + "…") if len(prompt) > self.max_chars else prompt
        return f"Draft based on prompt:\n{trimmed}\n\nCitations:\n{citations if citations else '- none found'}"
