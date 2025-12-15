"""Encoders and action spaces for the heuristic policy layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class SimpleStateEncoder:
    """Converts observations into a numeric vector suitable for placeholder policies."""

    def encode(self, observation: Dict) -> List[float]:
        features: List[float] = []
        features.append(float(len(observation.get("plan", []))))
        features.append(float(len(observation.get("constraints", []))))
        draft_len = len(str(observation.get("draft", "")))
        features.append(draft_len / 1024.0)
        goal_len = len(str(observation.get("goal", "")))
        features.append(goal_len / 256.0)
        return features or [0.0]


@dataclass
class RegistryBackedActionSpace:
    """Exposes registry tool names as action candidates."""

    actions_iterable: Iterable[str]

    def actions(self) -> Iterable[str]:
        return list(self.actions_iterable)
