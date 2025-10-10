# jarvis/agents/db_agent.py
import random
import datetime

# Mock database instances
mock_databases = [
    {
        "id": "db-001",
        "name": "CustomerDB",
        "engine": "PostgreSQL",
        "status": "running",   # changed from 'available' to 'running' for clarity
        "region": "us-east-1",
        "created_at": "2024-11-03",
        "size": "20 GB",
    },
    {
        "id": "db-002",
        "name": "AnalyticsDB",
        "engine": "MySQL",
        "status": "starting",  # changed from 'creating' to 'starting'
        "region": "us-west-2",
        "created_at": "2024-11-05",
        "size": "50 GB",
    },
    {
        "id": "db-003",
        "name": "AppMetrics",
        "engine": "Oracle",
        "status": "stopped",
        "region": "ap-south-1",
        "created_at": "2024-11-07",
        "size": "100 GB",
    },
]

def list_databases():
    """Return mock database instances for demo."""
    return mock_databases

def get_db_metrics(db_id):
    """Return random mock metrics for DB instance."""
    now = datetime.datetime.now()
    return {
        "CPU_Utilization": [random.uniform(10, 90) for _ in range(10)],
        "Storage_Usage_GB": [random.uniform(10, 50) for _ in range(10)],
        "Timestamps": [(now - datetime.timedelta(minutes=i)).strftime("%H:%M") for i in range(10)],
    }

# ------------------------------
# Start/Stop DB Actions (Mock)
# ------------------------------
def start_db(db_id):
    for db in mock_databases:
        if db["id"] == db_id:
            db["status"] = "running"
            return f"✅ Database {db_id} started successfully."
    return f"⚠️ Database {db_id} not found."

def stop_db(db_id):
    for db in mock_databases:
        if db["id"] == db_id:
            db["status"] = "stopped"
            return f"🛑 Database {db_id} stopped successfully."
    return f"⚠️ Database {db_id} not found."

# ------------------------------
# Helper to map status for UI
# ------------------------------
def is_db_running(db):
    """Return True if DB should show Stop button."""
    return db["status"].lower() in ["running", "available"]

def is_db_stopped(db):
    """Return True if DB should show Start button."""
    return db["status"].lower() in ["stopped", "starting", "creating"]
