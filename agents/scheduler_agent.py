# jarvis/agents/scheduler_agent.py
from datetime import datetime, timedelta

scheduled_tasks = []

def schedule_action(action_fn, delay_seconds, description):
    run_time = datetime.now() + timedelta(seconds=delay_seconds)
    task = {
        "id": f"task-{len(scheduled_tasks)+1}",
        "type": "Start" if "Start" in description else "Stop",
        "target": description.split()[-1],
        "run_time": run_time,
        "status": "pending",
        "action_fn": action_fn
    }
    scheduled_tasks.append(task)
    return task

def list_scheduled():
    # Return a copy without the actual function to avoid serialization issues in Streamlit
    return [
        {k: v for k, v in task.items() if k != "action_fn"} 
        for task in scheduled_tasks
    ]

def cancel_action(task_id):
    global scheduled_tasks
    scheduled_tasks = [t for t in scheduled_tasks if t["id"] != task_id]
