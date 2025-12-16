"""Command-line entry point to exercise the autonomous AR agent skeleton."""
from __future__ import annotations

import argparse
import json
from typing import List

from .config import AgentConfig
from .encoding import RegistryBackedActionSpace, SimpleStateEncoder
from .lam import IntentRecognizer, LAMPipeline, PerceptionEngine, TaskDecomposer
from .memory import EchoGenerator, InMemoryStore, SimpleRetriever
from .pipeline import BuildOrchestrator
from .planner import Planner
from .policy import ActionPolicy
from .rag import RetrievalAugmentedGenerator
from .tools import ToolExecutor, ToolRegistry


def register_default_tools(registry: ToolRegistry) -> None:
    """Register minimal tools to validate orchestration flow."""

    def noop_tool(payload):
        return {"success": True, "message": "No-op executed", "build_success": 1.0}

    def summarize_draft(payload):
        draft: str = payload.get("draft", "")
        return {
            "success": True,
            "message": f"Synthesized draft length {len(draft)}",
            "test_pass_rate": 1.0,
        }

    registry.register("noop", noop_tool)
    registry.register("summarize_draft", summarize_draft)


def build_orchestrator(initial_docs: List[str] | None = None) -> BuildOrchestrator:
    config = AgentConfig()
    store = InMemoryStore()
    if initial_docs:
        store.add(initial_docs)
    retriever = SimpleRetriever(store)
    generator = EchoGenerator()
    rag = RetrievalAugmentedGenerator(retriever=retriever, generator=generator)
    planner = Planner(memory=store)
    registry = ToolRegistry()
    register_default_tools(registry)
    action_space = RegistryBackedActionSpace(registry.available())
    policy = ActionPolicy(encoder=SimpleStateEncoder(), action_space=action_space)
    executor = ToolExecutor(registry)
    return BuildOrchestrator(config, planner, rag, policy, executor)


def build_lam(initial_docs: List[str] | None = None) -> LAMPipeline:
    orchestrator = build_orchestrator(initial_docs)
    perception = PerceptionEngine()
    recognizer = IntentRecognizer()
    decomposer = TaskDecomposer(orchestrator.planner)
    return LAMPipeline(
        perception=perception,
        intent_recognizer=recognizer,
        decomposer=decomposer,
        orchestrator=orchestrator,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an autonomous AR agent goal.")
    parser.add_argument("goal", help="High-level goal or feature request")
    parser.add_argument(
        "--constraint",
        action="append",
        default=[],
        help="Constraints to consider (repeatable)",
    )
    parser.add_argument(
        "--doc",
        action="append",
        default=[],
        help="Seed documents to prime retrieval",
    )
    args = parser.parse_args()

    lam = build_lam(initial_docs=args.doc)
    result, trace = lam.run(args.goal, constraints=args.constraint)
    print(
        json.dumps(
            {
                "success": result.success,
                "logs": result.logs,
                "rewards": result.rewards,
                "trace": {
                    "goal": trace.intent.goal,
                    "constraints": trace.intent.constraints,
                    "plan": [step.description for step in trace.plan],
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
