"""Large Action Model (LAM) autonomous pipeline stages."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .planner import PlanStep


@dataclass
class PerceptionOutput:
    """Signals gathered from the initial request and attachments."""

    raw_goal: str
    attachments: List[str] = field(default_factory=list)
    modalities: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)


class PerceptionStage:
    """Observe and normalize inputs across modalities."""

    def observe(self, goal: str, attachments: Iterable[str] | None = None) -> PerceptionOutput:
        attachment_list = list(attachments or [])
        modalities = ["text"]
        if attachment_list:
            modalities.append("attachment")
        observations = [goal, *attachment_list]
        return PerceptionOutput(
            raw_goal=goal,
            attachments=attachment_list,
            modalities=modalities,
            observations=observations,
        )


@dataclass
class IntentRecognitionOutput:
    goal: str
    intents: List[str]
    primary_intent: str
    confidence: float
    constraints: List[str]


class IntentRecognizer:
    """Identify the user's primary intent from perceived signals."""

    def recognize(
        self, perception: PerceptionOutput, constraints: Iterable[str] | None = None
    ) -> IntentRecognitionOutput:
        goal = perception.raw_goal.strip()
        intents = self._classify_intents(goal)
        primary = intents[0] if intents else "general_improvement"
        return IntentRecognitionOutput(
            goal=goal,
            intents=intents,
            primary_intent=primary,
            confidence=0.7 if intents else 0.5,
            constraints=list(constraints or []),
        )

    def _classify_intents(self, goal: str) -> List[str]:
        goal_lower = goal.lower()
        intents: List[str] = []
        if any(keyword in goal_lower for keyword in ["physics", "collision", "rigid"]):
            intents.append("physics")
        if any(keyword in goal_lower for keyword in ["animation", "timeline", "keyframe"]):
            intents.append("animation")
        if any(keyword in goal_lower for keyword in ["import", "fbx", "gltf", "usd"]):
            intents.append("asset_import")
        if any(keyword in goal_lower for keyword in ["export", "usdz", "glb", "share"]):
            intents.append("export")
        if any(keyword in goal_lower for keyword in ["occlusion", "lighting", "render"]):
            intents.append("rendering")
        if not intents:
            intents.append("general_improvement")
        return intents


@dataclass
class TaskDecompositionOutput:
    plan_steps: List[PlanStep]


class TaskDecomposer:
    """Break the intent into actionable ordered steps."""

    def __init__(self, planner):
        self.planner = planner

    def decompose(
        self, intent: IntentRecognitionOutput, constraints: Iterable[str] | None = None
    ) -> TaskDecompositionOutput:
        _ = constraints  # Constraints are passed downstream via planner context if needed.
        steps = self.planner.build_plan(intent.goal)
        return TaskDecompositionOutput(plan_steps=steps)


@dataclass
class ActionPlan:
    goal: str
    chosen_action: str
    observation: Dict
    draft: str
    retrieved_context: List[str]


class ActionPlannerWithMemory:
    """Fuse memory + RAG context and pick the next best action."""

    def __init__(self, rag, policy, memory_store):
        self.rag = rag
        self.policy = policy
        self.memory_store = memory_store

    def plan_and_select(
        self,
        intent: IntentRecognitionOutput,
        tasks: TaskDecompositionOutput,
        constraints: Iterable[str] | None = None,
    ) -> ActionPlan:
        retrieved = self.rag.retrieve(intent.goal, k=6)
        draft = self.rag.synthesize(intent.goal, constraints or intent.constraints)
        observation = {
            "goal": intent.goal,
            "constraints": list(constraints or intent.constraints),
            "intent": intent.primary_intent,
            "plan": [step.description for step in tasks.plan_steps],
            "draft": draft,
            "context": retrieved,
        }
        decision = self.policy.choose(observation)
        return ActionPlan(
            goal=intent.goal,
            chosen_action=decision.action,
            observation=observation,
            draft=draft,
            retrieved_context=retrieved,
        )


@dataclass
class ExecutionOutput:
    action: str
    payload: Dict
    output: Dict


class ExecutorStage:
    """Execute the chosen action with the orchestrator's tool executor."""

    def __init__(self, executor):
        self.executor = executor

    def execute(self, action_plan: ActionPlan) -> ExecutionOutput:
        payload = {"goal": action_plan.goal, "draft": action_plan.draft}
        output = self.executor.run(action_plan.chosen_action, payload)
        return ExecutionOutput(action=action_plan.chosen_action, payload=payload, output=output)


@dataclass
class LAMRun:
    perception: PerceptionOutput
    intent: IntentRecognitionOutput
    tasks: TaskDecompositionOutput
    action_plan: ActionPlan
    execution: ExecutionOutput


class LAMPipeline:
    """End-to-end autonomous pipeline following the LAM stages."""

    def __init__(
        self,
        perception: PerceptionStage,
        intent_recognizer: IntentRecognizer,
        decomposer: TaskDecomposer,
        action_planner: ActionPlannerWithMemory,
        executor: ExecutorStage,
    ):
        self.perception = perception
        self.intent_recognizer = intent_recognizer
        self.decomposer = decomposer
        self.action_planner = action_planner
        self.executor = executor

    def run(
        self, goal: str, constraints: Iterable[str] | None = None, attachments: Iterable[str] | None = None
    ) -> LAMRun:
        perception = self.perception.observe(goal, attachments)
        intent = self.intent_recognizer.recognize(perception, constraints)
        tasks = self.decomposer.decompose(intent, constraints)
        action_plan = self.action_planner.plan_and_select(intent, tasks, constraints)
        execution = self.executor.execute(action_plan)
        return LAMRun(
            perception=perception,
            intent=intent,
            tasks=tasks,
            action_plan=action_plan,
            execution=execution,
        )
