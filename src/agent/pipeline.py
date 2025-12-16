from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from .config import AgentConfig
from .lam import LAMPipeline, LAMRun
from .planner import Planner
from .policy import ActionPolicy
from .rag import RetrievalAugmentedGenerator
from .tools import ToolExecutor


@dataclass
class BuildResult:
    success: bool
    logs: str
    rewards: Dict[str, float]


class BuildOrchestrator:
    """Coordinates planning, RAG synthesis, policy selection, and tool execution."""

    def __init__(
        self,
        config: AgentConfig,
        planner: Planner,
        rag: RetrievalAugmentedGenerator,
        policy: ActionPolicy,
        executor: ToolExecutor,
        lam: LAMPipeline,
    ):
        self.config = config
        self.planner = planner
        self.rag = rag
        self.policy = policy
        self.executor = executor
        self.lam = lam

    def run_goal(
        self,
        goal: str,
        constraints: Iterable[str] | None = None,
        attachments: Iterable[str] | None = None,
    ) -> BuildResult:
        lam_result: LAMRun = self.lam.run(goal, constraints or [], attachments)
        tool_output = lam_result.execution.output
        reward = self._shape_reward(tool_output)
        self.policy.update_with_reward([tool_output], reward)
        return BuildResult(
            success=tool_output.get("success", False),
            logs=self._summarize_run(lam_result),
            rewards=reward,
        )

    def _shape_reward(self, tool_output: Dict) -> Dict[str, float]:
        reward = {}
        for key, weight in self.config.reward_weights.items():
            signal = float(tool_output.get(key, 0.0))
            reward[key] = signal * weight
        reward["total"] = sum(reward.values())
        return reward

    def _summarize_run(self, result: LAMRun) -> str:
        steps = " | ".join(step.description for step in result.tasks.plan_steps)
        return (
            f"Perception: modalities={result.perception.modalities}; "
            f"Intent: {result.intent.primary_intent}; "
            f"Tasks: {steps}; "
            f"Action: {result.action_plan.chosen_action}; "
            f"Tool output: {result.execution.output}"
        )
