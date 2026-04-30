import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("ticktick_cache.db")

def main():
    if not DB_PATH.exists():
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get projects
    cur = conn.execute("SELECT data_json FROM projects")
    projects_data = [json.loads(row["data_json"]) for row in cur.fetchall()]
    project_map = {p.get("id"): p.get("name") for p in projects_data}
    
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    # Local context date is 2026-04-29
    today_iso = "2026-04-29"
    
    in_scope_tasks = []
    
    for task in tasks:
        is_pinned = bool(task.get("pinnedTime") or task.get("pin") or task.get("isPinned") or task.get("pinned"))
        priority = task.get("priority", 0)
        is_high_priority = (priority == 5)
        
        due_date_str = task.get("dueDate", "")
        is_due_today_or_overdue = False
        if due_date_str and len(due_date_str) >= 10:
            if due_date_str[:10] <= today_iso:
                is_due_today_or_overdue = True
                
        repeat_flag = task.get("repeatFlag", "")
        is_recurring = bool(repeat_flag)
        
        start_date_str = task.get("startDate", "")
        is_all_day = task.get("isAllDay", True)
        has_explicit_time = bool(start_date_str and due_date_str and not is_all_day)
        
        if is_pinned or is_high_priority or is_due_today_or_overdue or is_recurring or has_explicit_time:
            # Classification Heuristics
            classification = "Needs review"
            destination = "Unknown"
            
            project_name = project_map.get(task.get("projectId"), "Inbox")
            
            if is_recurring and ("routine" in task.get("title", "").lower() or "block" in task.get("title", "").lower()):
                classification = "Apple Calendar event"
                destination = "Apple Calendar"
            elif has_explicit_time and not is_recurring:
                classification = "Needs review (Time Block?)"
                destination = "Both?"
            elif is_high_priority or is_pinned:
                classification = "Apple Reminder"
                destination = f"Apple Reminders ({project_name})"
            else:
                classification = "Apple Reminder"
                destination = f"Apple Reminders ({project_name})"
                
            # Formatting title to be single-line and pipe-safe for markdown table
            title = task.get("title", "")
            if not title:
                title = "(No Title)"
            title = str(title).replace("\n", " ").replace("\r", "").replace("|", "\\|")
            
            project_name = project_map.get(task.get("projectId"), "Inbox")
            
            reason = []
            if is_pinned: reason.append("Pinned")
            if is_high_priority: reason.append("High Priority")
            if is_due_today_or_overdue: reason.append("Due/Overdue")
            if is_recurring: reason.append("Recurring")
            if has_explicit_time: reason.append("Has Explicit Time")
            
            in_scope_tasks.append({
                "title": title,
                "project": project_name,
                "classification": classification,
                "destination": destination,
                "due_date": due_date_str,
                "recurrence": repeat_flag,
                "priority": priority,
                "reason": ", ".join(reason),
                "notes": "Verify classification"
            })
            
    # Sort tasks by project name, then priority, then due date
    in_scope_tasks.sort(key=lambda x: (x["project"], -x["priority"], x["due_date"]))
            
    # Write to Markdown
    md_path = Path("dry_run_table.md")
    with open(md_path, "w") as f:
        f.write("# Migration Dry Run\n\n")
        f.write(f"Total tasks in scope: {len(in_scope_tasks)}\n\n")
        f.write("| TickTick task | Source list/project | Classification | Destination | Due date/time | Recurrence | Priority | Proposed action | Notes / risk |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for t in in_scope_tasks:
            f.write(f"| {t['title']} | {t['project']} | {t['classification']} | {t['destination']} | {t['due_date']} | {t['recurrence']} | {t['priority']} | Migrate | Reason: {t['reason']}. {t['notes']} |\n")

    print(f"Successfully generated {md_path} with {len(in_scope_tasks)} tasks.")

if __name__ == "__main__":
    main()
