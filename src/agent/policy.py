from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Protocol


class StateEncoder(Protocol):
    def encode(self, observation: Dict) -> List[float]:
        ...


class ActionSpace(Protocol):
    def actions(self) -> Iterable[str]:
        ...


@dataclass
class PolicyDecision:
    action: str
    score: float
    rationale: str


class ActionPolicy:
    """Scores available actions using a learned policy."""

    def __init__(self, encoder: StateEncoder, action_space: ActionSpace):
        self.encoder = encoder
        self.action_space = action_space

    def choose(self, observation: Dict) -> PolicyDecision:
        encoded_state = self.encoder.encode(observation)
        candidates = list(self.action_space.actions())
        scored = self._score(encoded_state, candidates)
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[0]

    def _score(self, state: List[float], candidates: List[str]) -> List[PolicyDecision]:
        # Placeholder scoring: favors earlier actions but can be replaced by RL outputs.
        decisions: List[PolicyDecision] = []
        for idx, action in enumerate(candidates):
            score = 1.0 / (1 + idx)
            rationale = "Heuristic score; replace with policy network inference"
            decisions.append(PolicyDecision(action=action, score=score, rationale=rationale))
        return decisions

    def update_with_reward(self, trajectories: Iterable[Dict], reward: float) -> None:
        # Hook for RL algorithms (e.g., actor-critic, GRPO) to refine the policy.
        _ = trajectories, reward
        # Training loop intentionally omitted in skeleton.
