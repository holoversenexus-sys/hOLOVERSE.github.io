from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AgentConfig:
    """Configuration for the autonomous AR development agent."""

    model: str = "local-llm"
    embedding_model: str = "all-MiniLM-L6-v2"
    vector_store_uri: str = "http://localhost:6333"
    tools: List[str] = field(default_factory=lambda: ["git", "python", "unity-cli"])
    reward_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "build_success": 1.0,
            "test_pass_rate": 0.8,
            "frame_time_budget": 0.6,
            "tracking_stability": 0.7,
            "safety": 1.2,
        }
    )

    def telemetry_tags(self) -> Dict[str, str]:
        return {
            "agent": "holoverse-autonomous-ar",
            "model": self.model,
            "embedding_model": self.embedding_model,
        }
