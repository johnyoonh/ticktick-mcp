import json
import subprocess
from pathlib import Path
import os
import sys

def main():
    # Run prepare_batch.py to generate next_batch.json
    print("Preparing next batch...")
    subprocess.run(["python", "prepare_batch.py"], check=True)
    
    batch_file = Path("next_batch.json")
    if not batch_file.exists():
        print("No next_batch.json found.")
        return
        
    with open(batch_file, "r") as f:
        tasks = json.load(f)
        
    if not tasks:
        print("No tasks to migrate in this batch.")
        return
        
    print(f"Migrating {len(tasks)} tasks to Apple Reminders...")
    
    cli_path = "/Users/john/repos/mcp-server-apple-events/bin/EventKitCLI"
    
    log_file = Path("migration_log.md")
    
    # Read existing log to append
    with open(log_file, "a") as log:
        for t in tasks:
            title = t.get("title")
            targetList = t.get("targetList")
            priority = t.get("priority", 0)
            note = t.get("note", "")
            tags = t.get("tags", [])
            due_date = t.get("dueDate")
            orig_id = t.get("_original_id", "")
            orig_due = t.get("_original_due", "None")
            orig_list = t.get("_original_list", "Inbox")
            
            # Build command
            cmd = [cli_path, "--action", "create", "--title", title, "--targetList", targetList]
            if note:
                cmd.extend(["--note", note])
            if due_date:
                cmd.extend(["--dueDate", due_date])
            if priority:
                cmd.extend(["--priority", str(priority)])
                
            print(f"Migrating: {title[:50]}...")
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=True)
                out = json.loads(res.stdout)
                
                if out.get("status") == "success":
                    new_id = out["result"].get("id", "Created")
                    log.write(f"| 2026-04-29 | {orig_id} | {title.replace('|', '-')} | {orig_list} | {orig_due} | {targetList} | {new_id} | Success | {'Pinned' if 'pinned' in tags else ''} |\n")
                else:
                    print(f"Error migrating {title}: {out}")
                    log.write(f"| 2026-04-29 | {orig_id} | {title.replace('|', '-')} | {orig_list} | {orig_due} | {targetList} | FAILED | Error | |\n")
            except Exception as e:
                print(f"Failed to execute CLI for {title}: {e}")
                log.write(f"| 2026-04-29 | {orig_id} | {title.replace('|', '-')} | {orig_list} | {orig_due} | {targetList} | FAILED | Exception | |\n")
                
    print("Batch migration complete!")

if __name__ == "__main__":
    main()
