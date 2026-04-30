import sys
import os
from ticktick_web_api import TickTickWebClient
import datetime
import json

def main():
    client = TickTickWebClient()
    if not client.login():
        print("Failed to login to TickTick")
        sys.exit(1)
        
    tasks_data = client.get_all_tasks()
    if not tasks_data:
        print("Failed to get tasks")
        sys.exit(1)
        
    # Find sync tasks that have due dates
    sync_task_beans = tasks_data.get("syncTaskBean", {}).get("update", [])
    
    today_tasks = []
    
    # Get current date in UTC to compare with TickTick's due dates
    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime("%Y-%m-%dT") # Rough match
    
    # TickTick dates are typically ISO format like 2026-04-29T05:00:00.000+0000
    for task in sync_task_beans:
        # Skip completed or trashed tasks
        if task.get("status") == 2: # Completed
            continue
        if task.get("trashed"):
            continue
            
        due_date = task.get("startDate") or task.get("dueDate")
        if due_date:
            # Let's collect any task that has a due date
            # We'll print them first to see what's due
            today_tasks.append(task)
            
    print(f"Found {len(today_tasks)} active tasks with a due date.")
    for t in today_tasks[:10]:
        print(f" - {t.get('title')} (Due: {t.get('dueDate', t.get('startDate'))})")

if __name__ == "__main__":
    main()
