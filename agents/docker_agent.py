# agents/docker_agent.py
"""
Mock Docker Agent — handles Docker container operations.
Replace these mocks later with actual Docker SDK calls.
"""
import random
import datetime

mock_containers = [
    {"id": "c-001", "name": "nginx", "status": "running"},
    {"id": "c-002", "name": "redis", "status": "stopped"},
    {"id": "c-003", "name": "postgres", "status": "running"},
]


def list_containers():
    """Return mock list of containers."""
    return mock_containers


def start_container(container_id):
    """Mock start container."""
    for c in mock_containers:
        if c["id"] == container_id:
            c["status"] = "running"
            return f"✅ Container {container_id} started successfully."
    return f"⚠️ Container {container_id} not found."


def stop_container(container_id):
    """Mock stop container."""
    for c in mock_containers:
        if c["id"] == container_id:
            c["status"] = "stopped"
            return f"🛑 Container {container_id} stopped successfully."
    return f"⚠️ Container {container_id} not found."


# -----------------------------
# Mock container metrics
# -----------------------------
def get_container_metrics(container_id):
    """Return random mock metrics for container."""
    return {
        "CPU_Usage": [random.uniform(1, 80) for _ in range(10)],   # % CPU
        "Memory_Usage": [random.uniform(50, 500) for _ in range(10)],  # MB
    }

# -----------------------------
# Mock container logs
# -----------------------------
def get_container_logs(container_id, lines=50):
    """Return last N mock log lines for a container."""
    container_logs = {
        "c-001": ["nginx started", "request handled", "nginx stopped"],
        "c-002": ["redis started", "data cached", "redis stopped"],
        "c-003": ["postgres started", "query executed", "postgres stopped"],
    }
    logs = container_logs.get(container_id, [])
    return logs[-lines:]  # last N lines

