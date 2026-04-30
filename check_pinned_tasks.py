import sqlite3
import json
from pathlib import Path

DB_PATH = Path("ticktick_cache.db")

def main():
    if not DB_PATH.exists():
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    pinned_tasks = []
    for task in tasks:
        # Check for 'pinnedTime' field which seems to indicate a pinned task
        if task.get("pinnedTime"):
            pinned_tasks.append(task)
        elif task.get("pin") or task.get("isPinned") or task.get("pinned"):
            pinned_tasks.append(task)
        elif "pin" in json.dumps(task).lower():
            # If we find "pin" but not in a direct field, print it to investigate
            print(f"DEBUG: Found 'pin' in task JSON: {task.get('title')}")
            print(f"  JSON: {json.dumps(task)}")

    if not pinned_tasks:
        print("No explicitly pinned tasks found in DB.")
    else:
        print(f"Found {len(pinned_tasks)} pinned tasks:")
        for task in pinned_tasks:
            tags = task.get("tags", [])
            tag_str = f" [Tags: {', '.join(tags)}]" if tags else ""
            print(f"- {task.get('title')} (ID: {task.get('id')}){tag_str}")

if __name__ == "__main__":
    main()
