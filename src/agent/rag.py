from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol, Sequence


class Retriever(Protocol):
    def embed_and_search(self, query: str, k: int = 5) -> List[str]:
        ...

    def add_documents(self, documents: Iterable[str]) -> None:
        ...


class Generator(Protocol):
    def generate(self, prompt: str, context: Sequence[str]) -> str:
        ...


@dataclass
class RetrievalAugmentedGenerator:
    retriever: Retriever
    generator: Generator

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        return self.retriever.embed_and_search(query, k=k)

    def synthesize(self, goal: str, constraints: Sequence[str] | None = None) -> str:
        context = self.retrieve(goal, k=8)
        prompt = self._build_prompt(goal, constraints or [], context)
        return self.generator.generate(prompt, context)

    def _build_prompt(self, goal: str, constraints: Sequence[str], context: Sequence[str]) -> str:
        constraint_block = "\n".join(f"- {c}" for c in constraints)
        context_block = "\n".join(context)
        return (
            "Goal:\n" + goal + "\n\n"
            "Constraints:\n" + constraint_block + "\n\n"
            "Context:\n" + context_block + "\n\n"
            "Return a concise plan or patch with citations to the provided context when applicable."
        )
