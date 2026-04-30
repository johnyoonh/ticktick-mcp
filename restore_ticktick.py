import sys
sys.path.append('ticktick_mcp/src')
from ticktick_client import TickTickClient
import os
import json
from pathlib import Path
import sqlite3

def main():
    client = TickTickClient()
    client.login()
    print("Fetching all tasks from TickTick...")
    data = client._make_request("GET", "batch/check/0").json()
    if not data:
        print("Failed to fetch.")
        return
        
    sync_tasks = data.get("syncTaskBean", {}).get("update", [])
    
    # Let's find tasks that were recently modified and have status = -1 (deleted) or 2 (completed)
    # We will look for the 62 tasks that were modified in the clean_today_ticktick.py script.
    # Actually, we can read the original clean_today.py output or ticktick_cache.db to get the IDs.
    
    db_path = Path("ticktick_cache.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    cache_tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    # Find cache tasks due today or overdue
    today_iso = "2026-04-29"
    target_ids = set()
    for task in cache_tasks:
        due_date_str = task.get("dueDate", "")
        if due_date_str and due_date_str[:10] <= today_iso:
            target_ids.add(task.get("id"))
            
    print(f"Looking for {len(target_ids)} target IDs in sync data...")
    
    to_restore = []
    for t in sync_tasks:
        if t.get("id") in target_ids:
            # Check if it was deleted
            status = t.get("status")
            print(f"Task: {t.get('title')} | Status: {status} | Deleted: {t.get('isDeleted')} | projectId: {t.get('projectId')}")
            if status != 0 or t.get("isDeleted"):
                to_restore.append(t)
                
    print(f"Found {len(to_restore)} tasks to restore.")
    if not to_restore:
        return
        
    # To restore, we need to set status=0 and isDeleted=0 via the API wrapper.
    # The clean_today_ticktick.py used the TickTickClient from ticktick_mcp/src/ticktick_client.py
    import sys
    sys.path.append('ticktick_mcp/src')
    from ticktick_client import TickTickClient
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    tt_client = TickTickClient()
    tt_client.login()
    
    restore_payload = []
    for t in to_restore:
        restore_payload.append({
            "id": t["id"],
            "projectId": t["projectId"],
            "status": 0,
            "dueDate": None,
            "startDate": None
        })
        
    if restore_payload:
        res = tt_client._make_request("POST", "batch/task", json={"update": restore_payload})
        print(f"Restore response: {res.status_code}")

if __name__ == "__main__":
    main()
