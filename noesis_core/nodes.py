"""Small deterministic registry for the Noesis node topology."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Node:
    node_id: str
    role: str = "worker"
    online: bool = False
    last_seen: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def heartbeat(self, when: datetime | None = None) -> None:
        stamp = when or datetime.now(timezone.utc)
        self.last_seen = stamp.isoformat()
        self.online = True


class NodeRegistry:
    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}

    def register(self, node: Node) -> Node:
        if not node.node_id.strip():
            raise ValueError("node_id cannot be empty")
        self._nodes[node.node_id] = node
        return node

    def heartbeat(self, node_id: str, when: datetime | None = None) -> Node:
        node = self._nodes.get(node_id)
        if node is None:
            raise KeyError(node_id)
        node.heartbeat(when)
        return node

    def get(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def snapshot(self) -> tuple[Node, ...]:
        return tuple(self._nodes.values())

    def online_count(self) -> int:
        return sum(node.online for node in self._nodes.values())
