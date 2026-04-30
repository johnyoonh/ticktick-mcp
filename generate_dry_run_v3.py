import sqlite3
import json
import re
from pathlib import Path

DB_PATH = Path("ticktick_cache.db")

def clean_title(title):
    if not title:
        return "(No Title)"
    # First, completely remove markdown links that reference an .md file or an obsidian file tag
    # Example: "Task name [t/shopping.md](obsidian://...)" -> "Task name"
    title = re.sub(r'\s*\[[^\]]*\.md\]\([^)]+\)', '', title)
    
    # Second, for any other normal markdown links, extract just the text
    # Example: "[Video Title](https://youtube.com/...)" -> "Video Title"
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    
    # Clean up newlines
    title = str(title).replace("\n", " ").replace("\r", "").replace("|", "\\|").strip()
    return title

def assign_inbox_project(title):
    t = title.lower()
    if any(kw in t for kw in ["clean", "wash", "sweep", "trash", "organize", "vacuum", "laundry"]):
        return "cleaning"
    elif any(kw in t for kw in ["code", "script", "mcp", "api", "prompt", "ai", "build", "automation", "server", "python", "lucidchart"]):
        return "automation"
    elif any(kw in t for kw in ["read", "book", "study", "class", "course", "phd", "theology", "bible", "seminary", "missiology"]):
        return "education" # Seminary mapped to education
    else:
        # Default all other Inbox tasks to Home
        return "Home"

def main():
    if not DB_PATH.exists():
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT data_json FROM projects")
    projects_data = [json.loads(row["data_json"]) for row in cur.fetchall()]
    project_map = {p.get("id"): p.get("name") for p in projects_data}
    
    # Identify Active Projects
    active_project_keywords = ["automation", "home", "education", "cleaning"]
    active_project_ids = set()
    
    for pid, pname in project_map.items():
        for kw in active_project_keywords:
            if kw.lower() in pname.lower():
                active_project_ids.add(pid)
                
    # Ensure "education" handles "Seminary"
    # User wanted Seminary, mapping it to education based on TickTick list name.
    
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    today_iso = "2026-04-29"
    stale_cutoff = "2025-10-29T00:00:00" # 6 months ago
    
    in_scope_tasks = []
    
    for task in tasks:
        # Check staleness
        mod_time = task.get("modifiedTime") or task.get("createdTime") or ""
        if mod_time < stale_cutoff:
            continue
            
        pid = task.get("projectId")
        is_inbox = pid == "inbox120632618"
        
        title = clean_title(task.get("title", ""))
        
        # If in Inbox, assign to a project
        if is_inbox:
            assigned_kw = assign_inbox_project(title)
            # Find matching active project name
            mapped_name = next((pname for pid, pname in project_map.items() if assigned_kw.lower() in pname.lower() and pid in active_project_ids), assigned_kw.capitalize())
            project_name = mapped_name
            is_active_project = True # Because we forced it into an active project
        else:
            project_name = project_map.get(pid, "Unknown")
            is_active_project = pid in active_project_ids
            
            # Specifically map "education" to "Seminary" visually
            if "education" in project_name.lower():
                project_name = "Seminary (Education)"

        is_pinned = bool(task.get("pinnedTime") or task.get("pin") or task.get("isPinned") or task.get("pinned"))
        tt_priority = task.get("priority", 0)
        
        # New Priority Mapping for Apple Reminders (0=None, 1=High, 5=Medium, 9=Low)
        if is_pinned:
            apple_priority = 1 # High
        elif tt_priority == 5:
            apple_priority = 5 # Medium
        elif tt_priority == 3:
            apple_priority = 9 # Low
        else:
            apple_priority = 0 # None
            
        is_high_priority = (tt_priority == 5)
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
        
        if is_pinned or is_high_priority or is_due_today_or_overdue or is_recurring or has_explicit_time or is_active_project:
            classification = "Needs review"
            destination = "Unknown"
            action = "Migrate"
            
            if is_recurring and ("routine" in title.lower() or "block" in title.lower()):
                classification = "Apple Calendar event"
                destination = "Apple Calendar"
            elif has_explicit_time and not is_recurring:
                classification = "Needs review (Time Block?)"
                destination = "Both?"
            elif is_active_project:
                classification = "Apple Reminder"
                destination = f"Apple Reminders ({project_name})"
            else:
                classification = "Apple Reminder"
                destination = "Apple Reminders (Shelved)"
                apple_priority = 0
                action = "Migrate (Stripped Priority)"
                
            reason = []
            if is_pinned: reason.append("Pinned")
            if is_high_priority: reason.append("High Priority")
            if is_due_today_or_overdue: reason.append("Due/Overdue")
            if is_recurring: reason.append("Recurring")
            if has_explicit_time: reason.append("Explicit Time")
            if is_active_project: reason.append("Active Project")
            if not reason: reason.append("Active Project Default")
            
            in_scope_tasks.append({
                "title": title,
                "project": project_name,
                "classification": classification,
                "destination": destination,
                "due_date": due_date_str,
                "recurrence": repeat_flag,
                "priority": apple_priority,
                "action": action,
                "reason": ", ".join(reason)
            })
            
    in_scope_tasks.sort(key=lambda x: (x["destination"], -x["priority"], x["due_date"]))
            
    md_path = Path("dry_run_table_v3.md")
    with open(md_path, "w") as f:
        f.write("# Migration Dry Run v3 (Cleaned Titles & No Inbox)\n\n")
        f.write(f"Total tasks in scope: {len(in_scope_tasks)}\n\n")
        f.write("| TickTick task | Source list/project | Classification | Destination | Due date/time | Recurrence | Priority | Proposed action | Notes / risk |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for t in in_scope_tasks:
            f.write(f"| {t['title']} | {t['project']} | {t['classification']} | {t['destination']} | {t['due_date']} | {t['recurrence']} | {t['priority']} | {t['action']} | Reason: {t['reason']} |\n")

    print(f"Successfully generated {md_path} with {len(in_scope_tasks)} tasks.")

if __name__ == "__main__":
    main()
