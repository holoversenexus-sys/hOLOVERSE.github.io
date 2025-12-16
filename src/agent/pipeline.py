from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Sequence

from .config import AgentConfig
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
    ):
        self.config = config
        self.planner = planner
        self.rag = rag
        self.policy = policy
        self.executor = executor

    def run_goal(
        self,
        goal: str,
        constraints: Iterable[str] | None = None,
        plan: Sequence | None = None,
    ) -> BuildResult:
        steps = plan or self.planner.build_plan(goal)
        synthesis = self.rag.synthesize(goal, constraints or [])
        decision = self.policy.choose(
            {
                "goal": goal,
                "constraints": list(constraints or []),
                "plan": [getattr(step, "description", str(step)) for step in steps],
                "draft": synthesis,
            }
        )
        tool_output = self.executor.run(decision.action, {"goal": goal, "draft": synthesis})
        reward = self._shape_reward(tool_output)
        self.policy.update_with_reward([tool_output], reward)
        return BuildResult(success=tool_output.get("success", False), logs=str(tool_output), rewards=reward)

    def _shape_reward(self, tool_output: Dict) -> Dict[str, float]:
        reward = {}
        for key, weight in self.config.reward_weights.items():
            signal = float(tool_output.get(key, 0.0))
            reward[key] = signal * weight
        reward["total"] = sum(reward.values())
        return reward
