import ipaddress
import logging
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Any

from engine_helpers import read_config_data, update_config_data

logger = logging.getLogger("oes")


@dataclass
class ClusterNode:
    node_id: str
    host: str
    port: int
    weight: int = 1
    enabled: bool = True
    status: str = "unknown"
    latency_ms: float | None = None
    failures: int = 0
    last_checked: str | None = None
    source: str = "configured"


class ClusterManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cursor = 0

    def _nodes(self) -> list[ClusterNode]:
        raw_nodes = read_config_data().get("cluster_nodes", [])
        nodes = []
        for raw in raw_nodes:
            try:
                nodes.append(ClusterNode(**raw))
            except (TypeError, ValueError):
                logger.warning("cluster_node_invalid node=%r", raw)
        return nodes

    def _save_nodes(self, nodes: list[ClusterNode]) -> None:
        update_config_data({"cluster_nodes": [asdict(node) for node in nodes]})

    def status(self) -> dict[str, Any]:
        config = read_config_data()
        nodes = self._nodes()
        healthy = [node for node in nodes if node.enabled and node.status == "healthy"]
        primary = self.select_node(nodes)
        replicas = [node for node in healthy if not primary or node.node_id != primary.node_id]
        return {
            "enabled": str(config.get("cluster_enabled", "false")).lower() == "true",
            "discovery_cidr": config.get("cluster_discovery_cidr", ""),
            "discovery_port": config.get("cluster_discovery_port", 8000),
            "replication_mode": config.get("cluster_replication_mode", "primary-replica"),
            "nodes": [asdict(node) for node in nodes],
            "primary": asdict(primary) if primary else None,
            "replicas": [asdict(node) for node in replicas],
        }

    def check_node(self, node: ClusterNode, timeout: float = 0.5) -> ClusterNode:
        started = time.perf_counter()
        try:
            with socket.create_connection((node.host, node.port), timeout=timeout):
                node.status = "healthy"
                node.failures = 0
                node.latency_ms = round((time.perf_counter() - started) * 1000, 2)
        except OSError as error:
            node.status = "unhealthy"
            node.failures += 1
            node.latency_ms = None
            logger.warning("cluster_health_failed node=%s error=%s", node.node_id, error)
        node.last_checked = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return node

    def check_all(self) -> dict[str, Any]:
        nodes = self._nodes()
        with ThreadPoolExecutor(max_workers=min(16, max(1, len(nodes)))) as executor:
            checked = list(executor.map(self.check_node, nodes))
        self._save_nodes(checked)
        logger.info("cluster_health_checked nodes=%s", len(checked))
        return self.status()

    def discover(self, cidr: str, port: int, timeout: float = 0.25) -> dict[str, Any]:
        network = ipaddress.ip_network(cidr, strict=False)
        hosts = list(network.hosts())
        if len(hosts) > 254:
            raise ValueError("Discovery is limited to 254 hosts per request")
        existing = {node.node_id: node for node in self._nodes()}
        candidates = [ClusterNode(f"{host}:{port}", str(host), port, source="discovered") for host in hosts]
        with ThreadPoolExecutor(max_workers=min(32, max(1, len(candidates)))) as executor:
            futures = {executor.submit(self.check_node, node, timeout): node for node in candidates}
            for future in as_completed(futures):
                node = future.result()
                if node.status == "healthy":
                    existing[node.node_id] = node
        discovered = list(existing.values())
        self._save_nodes(discovered)
        logger.info("cluster_discovered cidr=%s port=%s nodes=%s", cidr, port, len(discovered))
        return self.status()

    def select_node(self, nodes: list[ClusterNode] | None = None) -> ClusterNode | None:
        candidates = [node for node in (nodes or self._nodes()) if node.enabled and node.status == "healthy"]
        if not candidates:
            return None
        weighted = [node for node in candidates for _ in range(max(1, node.weight))]
        with self._lock:
            node = weighted[self._cursor % len(weighted)]
            self._cursor += 1
        return node


cluster_manager = ClusterManager()
