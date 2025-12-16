"""Autonomous AR development agent package."""

from .cli import build_orchestrator, register_default_tools
from .config import AgentConfig
from .encoding import RegistryBackedActionSpace, SimpleStateEncoder
from .lam import (
    ActionPlannerWithMemory,
    ExecutorStage,
    IntentRecognizer,
    LAMPipeline,
    PerceptionStage,
    TaskDecomposer,
)
from .memory import EchoGenerator, InMemoryStore, SimpleRetriever
from .pipeline import BuildOrchestrator
from .planner import Planner, PlanStep
from .policy import ActionPolicy, PolicyDecision
from .rag import RetrievalAugmentedGenerator
from .tools import ToolExecutor, ToolRegistry

__all__ = [
    "ActionPolicy",
    "AgentConfig",
    "BuildOrchestrator",
    "EchoGenerator",
    "ExecutorStage",
    "InMemoryStore",
    "IntentRecognizer",
    "LAMPipeline",
    "PerceptionStage",
    "Planner",
    "PlanStep",
    "PolicyDecision",
    "RegistryBackedActionSpace",
    "RetrievalAugmentedGenerator",
    "SimpleRetriever",
    "SimpleStateEncoder",
    "TaskDecomposer",
    "ActionPlannerWithMemory",
    "ToolExecutor",
    "ToolRegistry",
    "build_orchestrator",
    "register_default_tools",
]
