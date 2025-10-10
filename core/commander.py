from brains.ollama_ai import OllamaAI
from agents import aws_agent, db_agent, docker_agent, logs_agent
import re

ai_brain = OllamaAI(model="llama2")

def parse_command(user_input: str) -> dict:
    command = user_input.lower().strip()

    # -----------------------
    # All Servers
    # -----------------------
    if "list all servers" in command:
        return {"action": "list_all_servers"}

    # -----------------------
    # Logs commands
    # -----------------------
    elif command.startswith("show"):
        # Extract level (ERROR, WARNING, INFO, ALL)
        level = None
        if "error" in command:
            level = "ERROR"
        elif "warning" in command:
            level = "WARNING"
        elif "info" in command:
            level = "INFO"
        else:
            level = "ALL"

        # Extract files if specified
        files = None
        if "from" in command:
            try:
                files_part = command.split("from")[1].strip()
                files = [f.strip() for f in files_part.split(",")]
            except:
                files = None

        return {"action": "show_logs", "level": level, "files": files}

    elif command.startswith("create ticket"):
        # Extract files if specified
        files = None
        if "in" in command:
            try:
                files_part = command.split("in")[1].strip()
                files = [f.strip() for f in files_part.split(",")]
            except:
                files = None
        return {"action": "create_ticket_from_error", "files": files}

    elif "list tickets" in command:
        return {"action": "list_tickets"}

    # -----------------------
    # EC2
    # -----------------------
    elif "list ec2" in command:
        return {"action": "list_ec2"}
    elif "start ec2" in command:
        return {"action": "start_ec2", "instance_id": extract_instance_id(command)}
    elif "stop ec2" in command:
        return {"action": "stop_ec2", "instance_id": extract_instance_id(command)}

    # -----------------------
    # DB
    # -----------------------
    elif "list db" in command or "list database" in command:
        return {"action": "list_db"}
    elif "start db" in command:
        return {"action": "start_db", "db_id": extract_instance_id(command)}
    elif "stop db" in command:
        return {"action": "stop_db", "db_id": extract_instance_id(command)}

    # -----------------------
    # Docker
    # -----------------------
    elif "list container" in command:
        return {"action": "list_container"}
    elif "start container" in command:
        return {"action": "start_container", "cid": extract_instance_id(command)}
    elif "stop container" in command:
        return {"action": "stop_container", "cid": extract_instance_id(command)}

    # -----------------------
    # Unknown / AI
    # -----------------------
    else:
        response = ai_brain.ask(f"Convert this into Jarvis action JSON:\n{user_input}")
        return {"action": "unknown", "message": response}


def extract_instance_id(text: str) -> str:
    match = re.search(r"[a-z0-9\-]+", text)
    return match.group(0) if match else ""
