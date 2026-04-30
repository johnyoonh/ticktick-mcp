import sqlite3
import json
import re
from pathlib import Path

DB_PATH = Path("ticktick_cache.db")
LOG_PATH = Path("migration_log.md")

def clean_title(title):
    if not title: return "(No Title)"
    title = re.sub(r'\s*\[[^\]]*\.md\]\([^)]+\)', '', title)
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    title = str(title).replace("\n", " ").replace("\r", "").strip()
    return title

def assign_inbox_project(title):
    t = title.lower()
    if any(kw in t for kw in ["clean", "wash", "sweep", "trash", "organize", "vacuum", "laundry"]): return "Cleaning"
    elif any(kw in t for kw in ["code", "script", "mcp", "api", "prompt", "ai", "build", "automation", "server", "python", "lucidchart"]): return "Automation"
    elif any(kw in t for kw in ["read", "book", "study", "class", "course", "phd", "theology", "bible", "seminary", "missiology"]): return "Seminary (Education)"
    else: return "Home"

def get_migrated_ids():
    if not LOG_PATH.exists(): return set()
    migrated = set()
    with open(LOG_PATH, "r") as f:
        for line in f:
            if "|" in line:
                parts = line.split("|")
                if len(parts) > 2 and parts[2].strip() and "Original ID" not in parts[2]:
                    migrated.add(parts[2].strip())
    return migrated

def main():
    migrated_ids = get_migrated_ids()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT data_json FROM projects")
    project_map = {json.loads(row["data_json"]).get("id"): json.loads(row["data_json"]).get("name") for row in cur.fetchall()}
    
    active_project_keywords = ["automation", "home", "education", "cleaning"]
    active_project_ids = {pid for pid, pname in project_map.items() if any(kw.lower() in pname.lower() for kw in active_project_keywords)}
    
    cur = conn.execute("SELECT data_json FROM tasks WHERE is_deleted = 0")
    tasks = [json.loads(row["data_json"]) for row in cur.fetchall()]
    
    today_iso = "2026-04-29"
    stale_cutoff = "2025-10-29T00:00:00"
    
    batch = []
    
    for task in tasks:
        task_id = task.get("id")
        if task_id in migrated_ids: continue
        
        mod_time = task.get("modifiedTime") or task.get("createdTime") or ""
        if mod_time < stale_cutoff: continue
            
        pid = task.get("projectId")
        is_inbox = pid == "inbox120632618"
        title = clean_title(task.get("title", ""))
        
        if is_inbox:
            project_name = assign_inbox_project(title)
            is_active_project = True
        else:
            project_name = project_map.get(pid, "Unknown")
            if "education" in project_name.lower(): project_name = "Seminary (Education)"
            is_active_project = pid in active_project_ids

        is_pinned = bool(task.get("pinnedTime") or task.get("pin") or task.get("isPinned") or task.get("pinned"))
        tt_priority = task.get("priority", 0)
        
        if is_pinned: apple_priority = 1
        elif tt_priority == 5: apple_priority = 5
        elif tt_priority == 3: apple_priority = 9
        else: apple_priority = 0
            
        due_date_str = task.get("dueDate", "")
        has_explicit_time = bool(task.get("startDate", "") and due_date_str and not task.get("isAllDay", True))
        is_recurring = bool(task.get("repeatFlag", ""))
        
        if is_pinned or (tt_priority == 5) or (due_date_str and due_date_str[:10] <= today_iso) or is_recurring or has_explicit_time or is_active_project:
            destination = project_name if is_active_project else "Shelved"
            if destination == "Shelved": apple_priority = 0
            if is_recurring and ("routine" in title.lower() or "block" in title.lower()): continue # Skip Calendar items for this batch script
            
            tags = ["migrated-ticktick"]
            if is_pinned: tags.append("pinned")
            for t in task.get("tags", []): tags.append(t.replace(" ", "-").replace("/", "-").lower())
            
            notes = f"Migrated from TickTick\nMIGRATION_BATCH: ticktick-to-apple-2026-04-29\nOriginal TickTick title: {task.get('title', '')}\nOriginal list/project: {project_map.get(pid, 'Inbox')}\nOriginal priority: {tt_priority}\nOriginal due date: {due_date_str}\nOriginal URL or ID, if available: {task_id}\nOriginal notes: {task.get('content', '')}"
            
            # Format due date if exists: YYYY-MM-DD HH:mm:ss
            fmt_due = None
            if due_date_str:
                # TickTick format: "2026-04-15T05:00:00.000+0000"
                try:
                    fmt_due = due_date_str[:10] + " " + due_date_str[11:19]
                except:
                    pass

            batch.append({
                "action": "create",
                "title": title,
                "targetList": destination,
                "priority": apple_priority,
                "tags": tags,
                "note": notes,
                "dueDate": None,
                "_original_id": task_id,
                "_original_due": due_date_str,
                "_original_list": project_map.get(pid, "Inbox")
            })
            
            if len(batch) >= 25: break

    with open("next_batch.json", "w") as f:
        json.dump(batch, f, indent=2)
    print(f"Generated next_batch.json with {len(batch)} tasks")

if __name__ == "__main__":
    main()
