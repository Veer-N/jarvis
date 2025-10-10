import os
from pathlib import Path

# -------------------------------
# Configuration / Demo Setup
# -------------------------------
LOG_DIR = Path("mock_logs")
LOG_DIR.mkdir(exist_ok=True)

available_logs = ["app1.log", "app2.log", "db.log"]
for file in available_logs:
    f = LOG_DIR / file
    if not f.exists():
        f.write_text(
            "2025-09-28 09:00 ERROR App failed to start\n"
            "2025-09-28 09:05 WARNING High CPU usage\n"
            "2025-09-28 09:10 INFO Service restarted\n"
        )

# Track last read positions for incremental reads
last_read_positions = {file: 0 for file in available_logs}
mock_tickets = []

# -------------------------------
# Utility Functions
# -------------------------------

def read_new_logs(file_name: str, level: str = None):
    """Read only new lines from a file, optionally filtered by level."""
    path = LOG_DIR / file_name
    if not path.exists():
        return []

    lines = path.read_text().splitlines()
    start = last_read_positions[file_name]
    new_lines = lines[start:]
    last_read_positions[file_name] = len(lines)

    # Filter by log level
    if level and level.upper() != "ALL":
        new_lines = [l for l in new_lines if level.upper() in l]

    return new_lines


def read_all_logs(file_name: str, level: str = None):
    """Read all lines from a file, optionally filtered by level."""
    path = LOG_DIR / file_name
    if not path.exists():
        return []

    lines = path.read_text().splitlines()

    if level and level.upper() != "ALL":
        lines = [l for l in lines if level.upper() in l]

    return lines


def show_logs(level: str = None, files: list = None, all_logs=False):
    """
    Return logs from multiple files with optional level filtering.
    If all_logs=True, ignore last_read_positions.
    """
    if files is None:
        files = available_logs

    logs = {}
    for f in files:
        path = LOG_DIR / f
        if not path.exists():
            logs[f] = []
            continue

        lines = path.read_text().splitlines()

        # Decide which lines to return
        if all_logs:
            selected_lines = lines
        else:
            start = last_read_positions[f]
            selected_lines = lines[start:]
            last_read_positions[f] = len(lines)

        # Apply level filtering
        if level and level.upper() != "ALL":
            selected_lines = [l for l in selected_lines if level.upper() in l]

        logs[f] = selected_lines

    return logs


def create_ticket_from_error(files: list = None):
    """
    Scan ERROR logs in the given files and create tickets for new errors.
    Ensures each log line creates only one ticket per file.
    """
    if files is None:
        files = available_logs

    created = []

    for f in files:
        error_lines = read_all_logs(f, "ERROR")
        for line in error_lines:
            # Skip if a ticket already exists for this file + message
            exists = any(
                t.get("source") == f and t.get("message") == line for t in mock_tickets
            )
            if exists:
                continue

            ticket_id = f"TICKET-{len(mock_tickets)+1}"
            ticket = {
                "id": ticket_id,
                "source": f,
                "summary": line,
                "message": line,
                "status": "OPEN"
            }
            mock_tickets.append(ticket)
            created.append(ticket)

    return created


def list_tickets():
    """Return all created tickets."""
    return mock_tickets
