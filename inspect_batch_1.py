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
    
    # We want to fetch the first 5 tasks from the dry run table to inspect their raw JSON
    # so we know exactly what we are sending to Apple Reminders
    
    titles_to_find = [
        "Returns: Costco Online",
        "45m Chase Correspondance",
        "30m Loss of Use $2000",
        "Email TopGolf Coporate office for refund $400",
        "Get better at using Lucidchart"
    ]
    
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    found_tasks = []
    for task in tasks:
        title = task.get("title", "").replace("\n", " ").replace("\r", "").strip()
        for target in titles_to_find:
            if target.lower() in title.lower():
                found_tasks.append(task)
                break
                
    for i, t in enumerate(found_tasks[:5]):
        print(f"--- Task {i+1} ---")
        print(json.dumps(t, indent=2))
        print()

if __name__ == "__main__":
    main()
