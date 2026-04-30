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
    
    cur = conn.execute("SELECT data_json FROM projects")
    projects_data = [json.loads(row["data_json"]) for row in cur.fetchall()]
    project_map = {p.get("id"): p.get("name") for p in projects_data}
    
    # Map user inputs to actual project IDs
    active_project_keywords = ["automation", "home", "seminary", "cleaning"]
    active_project_ids = set(["inbox120632618"])  # Inbox is always active in a way, but maybe not a true "project"
    
    for pid, pname in project_map.items():
        for kw in active_project_keywords:
            if kw.lower() in pname.lower():
                active_project_ids.add(pid)
                
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    today_iso = "2026-04-29"
    stale_cutoff = "2025-10-29T00:00:00" # 6 months ago
    
    in_scope_tasks = []
    
    for task in tasks:
        # Check staleness based on modifiedTime (or createdTime if missing)
        mod_time = task.get("modifiedTime") or task.get("createdTime") or ""
        if mod_time < stale_cutoff:
            continue # Ignore entirely
            
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
        
        pid = task.get("projectId")
        project_name = project_map.get(pid, "Inbox")
        is_active_project = pid in active_project_ids
        
        if is_pinned or is_high_priority or is_due_today_or_overdue or is_recurring or has_explicit_time or is_active_project:
            # Classification Heuristics
            classification = "Needs review"
            destination = "Unknown"
            action = "Migrate"
            
            if is_recurring and ("routine" in task.get("title", "").lower() or "block" in task.get("title", "").lower()):
                classification = "Apple Calendar event"
                destination = "Apple Calendar"
            elif has_explicit_time and not is_recurring:
                classification = "Needs review (Time Block?)"
                destination = "Both?"
            elif is_active_project or pid == "inbox120632618":
                classification = "Apple Reminder"
                destination = f"Apple Reminders ({project_name})"
            else:
                # Task is in a shelved project
                classification = "Apple Reminder"
                destination = "Apple Reminders (Shelved)"
                priority = 0 # Strip priority from shelved items
                action = "Migrate (Stripped Priority)"
                
            title = task.get("title", "")
            if not title:
                title = "(No Title)"
            title = str(title).replace("\n", " ").replace("\r", "").replace("|", "\\|")
            
            reason = []
            if is_pinned: reason.append("Pinned")
            if is_high_priority: reason.append("High Priority")
            if is_due_today_or_overdue: reason.append("Due/Overdue")
            if is_recurring: reason.append("Recurring")
            if has_explicit_time: reason.append("Explicit Time")
            if is_active_project: reason.append("Active Project")
            
            if not reason:
                reason.append("Active Project Default")
            
            in_scope_tasks.append({
                "title": title,
                "project": project_name,
                "classification": classification,
                "destination": destination,
                "due_date": due_date_str,
                "recurrence": repeat_flag,
                "priority": priority,
                "action": action,
                "reason": ", ".join(reason),
                "notes": "Verify classification"
            })
            
    in_scope_tasks.sort(key=lambda x: (x["destination"], -x["priority"], x["due_date"]))
            
    md_path = Path("dry_run_table_v2.md")
    with open(md_path, "w") as f:
        f.write("# Migration Dry Run v2 (Filtered by Active Projects & Staleness)\n\n")
        f.write(f"Total tasks in scope: {len(in_scope_tasks)}\n\n")
        f.write("| TickTick task | Source list/project | Classification | Destination | Due date/time | Recurrence | Priority | Proposed action | Notes / risk |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for t in in_scope_tasks:
            f.write(f"| {t['title']} | {t['project']} | {t['classification']} | {t['destination']} | {t['due_date']} | {t['recurrence']} | {t['priority']} | {t['action']} | Reason: {t['reason']} |\n")

    print(f"Successfully generated {md_path} with {len(in_scope_tasks)} tasks.")

if __name__ == "__main__":
    main()
