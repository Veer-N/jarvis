import json
from pathlib import Path
from datetime import datetime

# -------------------------------
# Configuration / Demo Setup
# -------------------------------
REGISTRY_FILE = Path("mock_jira_tickets.json")
REGISTRY_FILE.touch(exist_ok=True)

# Sample tickets structure
# [
#     {
#         "id": "TICKET-1",
#         "summary": "App failed to start",
#         "source": "app1.log",
#         "status": "OPEN",
#         "user": "veer",
#         "jira_link": "https://jira.company.com/browse/TICKET-1",
#         "timestamp": "2025-10-10 15:10"
#     }
# ]

# -------------------------------
# Helper Functions
# -------------------------------

def load_tickets():
    if REGISTRY_FILE.exists() and REGISTRY_FILE.stat().st_size > 0:
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)
    return []


def save_tickets(tickets):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(tickets, f, indent=2)


# -------------------------------
# API Functions
# -------------------------------

def list_tickets(user_only=True, open_only=True, current_user="veer"):
    """
    Return tickets filtered by:
    - user_only: tickets belonging to the current user
    - open_only: tickets with status OPEN
    """
    tickets = load_tickets()
    filtered = []

    for t in tickets:
        if user_only and t.get("user") != current_user:
            continue
        if open_only and t.get("status") != "OPEN":
            continue
        filtered.append(t)
    return filtered


def create_ticket(summary, source, user="veer"):
    """
    Create a new ticket with unique ID and Jira link.
    """
    tickets = load_tickets()
    ticket_id = f"TICKET-{len(tickets)+1}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    jira_link = f"https://jira.company.com/browse/{ticket_id}"

    ticket = {
        "id": ticket_id,
        "summary": summary,
        "source": source,
        "status": "OPEN",
        "user": user,
        "jira_link": jira_link,
        "timestamp": timestamp
    }

    tickets.append(ticket)
    save_tickets(tickets)
    return ticket


def close_ticket(ticket_id):
    """
    Close a ticket by ID. Updates the local registry.
    """
    tickets = load_tickets()
    for t in tickets:
        if t["id"] == ticket_id:
            t["status"] = "CLOSED"
            break
    save_tickets(tickets)
