# agents/aws_agent.py

# Mock EC2 instances
mock_ec2_instances = [
    {"id": "i-001", "name": "WebServer", "state": "stopped"},
    {"id": "i-002", "name": "DBServer", "state": "running"},
    {"id": "i-003", "name": "AppServer", "state": "stopped"},
]

def list_ec2_instances():
    return mock_ec2_instances

def start_ec2(instance_id):
    for inst in mock_ec2_instances:
        if inst["id"] == instance_id:
            inst["state"] = "running"
            return f"EC2 {instance_id} started"
    return f"EC2 {instance_id} not found"

def stop_ec2(instance_id):
    for inst in mock_ec2_instances:
        if inst["id"] == instance_id:
            inst["state"] = "stopped"
            return f"EC2 {instance_id} stopped"
    return f"EC2 {instance_id} not found"
