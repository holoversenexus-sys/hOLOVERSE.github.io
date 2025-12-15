from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List

ToolFn = Callable[[Dict], Dict]


@dataclass
class ToolRegistry:
    tools: Dict[str, ToolFn] = field(default_factory=dict)

    def register(self, name: str, fn: ToolFn) -> None:
        self.tools[name] = fn

    def available(self) -> Iterable[str]:
        return self.tools.keys()

    def invoke(self, name: str, payload: Dict) -> Dict:
        if name not in self.tools:
            raise KeyError(f"Tool {name} is not registered")
        return self.tools[name](payload)


class ToolExecutor:
    """Executes registered tools and tracks outcomes."""

    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or ToolRegistry()
        self.invocation_log: List[Dict] = []

    def run(self, tool_name: str, payload: Dict) -> Dict:
        result = self.registry.invoke(tool_name, payload)
        self.invocation_log.append({"tool": tool_name, "payload": payload, "result": result})
        return result

    def summary(self) -> List[Dict]:
        return list(self.invocation_log)
