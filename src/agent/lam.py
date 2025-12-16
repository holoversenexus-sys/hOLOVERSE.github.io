"""Large Action Model (LAM) pipeline aligned with perception → intent → tasks → plan/execute."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .pipeline import BuildOrchestrator, BuildResult
from .planner import PlanStep, Planner


@dataclass
class Observation:
    """Structured perception output from raw user input or multi-modal payloads."""

    modality: str
    raw: str
    tokens: List[str]
    metadata: Dict


@dataclass
class Intent:
    goal: str
    constraints: List[str]


@dataclass
class LAMTrace:
    observation: Observation
    intent: Intent
    plan: List[PlanStep]


class PerceptionEngine:
    """Parses raw input into an observation the downstream stages can consume."""

    def observe(self, raw_input: str, metadata: Dict | None = None) -> Observation:
        meta = metadata or {}
        tokens = raw_input.split()
        modality = meta.get("modality", "text")
        return Observation(modality=modality, raw=raw_input, tokens=tokens, metadata=meta)


class IntentRecognizer:
    """Derives a goal and constraints from the perceived observation."""

    def recognize(self, observation: Observation, extra_constraints: Iterable[str] | None = None) -> Intent:
        lines = [line.strip() for line in observation.raw.splitlines() if line.strip()]
        goal = lines[0] if lines else observation.raw
        constraints: List[str] = []
        for line in lines[1:]:
            normalized = line.lower()
            if normalized.startswith("constraint:"):
                constraints.append(line.split(":", 1)[-1].strip())
            elif normalized.startswith("- "):
                constraints.append(line[2:].strip())
            elif "must" in normalized or "should" in normalized:
                constraints.append(line)
        if extra_constraints:
            constraints.extend(list(extra_constraints))
        return Intent(goal=goal, constraints=constraints)


class TaskDecomposer:
    """Breaks a goal into plan steps by calling the planner."""

    def __init__(self, planner: Planner):
        self.planner = planner

    def decompose(self, intent: Intent) -> List[PlanStep]:
        return self.planner.build_plan(intent.goal)


class LAMPipeline:
    """Implements the LAM flow through perception → intent → tasks → plan/execute."""

    def __init__(
        self,
        perception: PerceptionEngine,
        intent_recognizer: IntentRecognizer,
        decomposer: TaskDecomposer,
        orchestrator: BuildOrchestrator,
    ):
        self.perception = perception
        self.intent_recognizer = intent_recognizer
        self.decomposer = decomposer
        self.orchestrator = orchestrator

    def run(
        self,
        raw_input: str,
        metadata: Dict | None = None,
        constraints: Iterable[str] | None = None,
    ) -> Tuple[BuildResult, LAMTrace]:
        observation = self.perception.observe(raw_input, metadata)
        intent = self.intent_recognizer.recognize(observation, extra_constraints=constraints)
        plan = self.decomposer.decompose(intent)
        result = self.orchestrator.run_goal(intent.goal, intent.constraints, plan=plan)
        return result, LAMTrace(observation=observation, intent=intent, plan=plan)
