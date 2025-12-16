from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol


class MemoryStore(Protocol):
    def retrieve(self, query: str, k: int = 5) -> List[str]:
        ...


@dataclass
class PlanStep:
    description: str
    rationale: str
    dependencies: List[str] | None = None


class Planner:
    """Transforms goals into ordered plan steps with retrieved context."""

    def __init__(self, memory: MemoryStore):
        self.memory = memory

    def build_plan(self, goal: str) -> List[PlanStep]:
        context = self.memory.retrieve(goal, k=5)
        steps = [
            PlanStep(
                description="Gather context and constraints",
                rationale="Ensure actions are grounded in recent decisions and docs.",
            ),
            PlanStep(
                description="Draft implementation or patch",
                rationale="Use RAG to synthesize changes aligned with constraints.",
                dependencies=["Gather context and constraints"],
            ),
            PlanStep(
                description="Run build and targeted tests",
                rationale="Validate correctness and performance early.",
                dependencies=["Draft implementation or patch"],
            ),
            PlanStep(
                description="Evaluate telemetry and update policy",
                rationale="Feed rewards back into RL policy for continual improvement.",
                dependencies=["Run build and targeted tests"],
            ),
        ]
        if context:
            steps.insert(
                1,
                PlanStep(
                    description="Integrate retrieved exemplars",
                    rationale="Ground plan on nearest-neighbor solutions and patterns.",
                    dependencies=["Gather context and constraints"],
                ),
            )
        return steps
