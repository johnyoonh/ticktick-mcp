import os
import sys
import sqlite3
import json
import datetime
from pathlib import Path

# Add the ticktick-mcp directory to the python path
sys.path.insert(0, str(Path.cwd()))
from ticktick_mcp.src.ticktick_client import TickTickClient

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
    
    # Initialize TickTick client
    try:
        client = TickTickClient()
    except Exception as e:
        print(f"Failed to initialize TickTick client: {e}")
        return
        
    count = 0
    for t in overdue_or_today:
        task_id = t.get('id')
        project_id = t.get('projectId')
        title = t.get('title')
        
        print(f"Clearing due date for: {title}")
        
        # We construct the update payload manually to ensure dueDate is null/empty
        # to clear it from the task.
        data = {
            "id": task_id,
            "projectId": project_id,
            "dueDate": None,
            "startDate": None,
            "isAllDay": False
        }
        
        # Also need to send the title
        if title:
            data["title"] = title
            
        try:
            res = client._make_request("POST", f"/task/{task_id}", data)
            # If no error in res
            if "error" in res:
                print(f"Error updating {title}: {res['error']}")
            else:
                count += 1
        except Exception as e:
            print(f"Failed to update {title}: {e}")
            
    print(f"Successfully cleared due dates for {count} tasks.")

if __name__ == "__main__":
    main()
