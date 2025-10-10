import os, json, shutil
from datetime import datetime

def save_report(report: dict, name: str):
    filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = f"reports/{filename}"
    archive_path = f"reports/archive/{filename}"
    os.makedirs("reports/archive", exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    shutil.copy(path, archive_path)
