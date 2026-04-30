import sqlite3
import json
import datetime
from pathlib import Path

DB_PATH = Path("ticktick_cache.db")

def main():
    if not DB_PATH.exists():
        print("DB not found")
        return
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    now = datetime.datetime.now(datetime.timezone.utc)
    today_iso = now.strftime("%Y-%m-%d")
    
    overdue_or_today = []
    
    for task in tasks:
        due_date_str = task.get("dueDate", "")
        if due_date_str:
            date_part = due_date_str[:10]
            if date_part <= today_iso:
                overdue_or_today.append(task)
                
    print(f"Found {len(overdue_or_today)} tasks due today or overdue in cache.")
    for t in overdue_or_today[:10]:
        print(f" - {t.get('title')} (Due: {t.get('dueDate')})")

if __name__ == "__main__":
    main()
