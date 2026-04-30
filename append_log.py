import json
from pathlib import Path
import re

LOG_PATH = Path("migration_log.md")

def strip_emojis(text):
    if not text: return ""
    return re.sub(r'[^\w\s.,;:!?\'"()-]', '', text)

def main():
    with open("next_batch.json", "r") as f:
        batch = json.load(f)
        
    log_entries = []
    for t in batch:
        original_id = t.get("_original_id", "")
        title = strip_emojis(t.get("title", ""))
        original_list = t.get("_original_list", "Inbox")
        due = t.get("_original_due", "None")
        dest_list = t.get("targetList", "Unknown")
        tags = t.get("tags", [])
        
        # Priority mapping is in Apple format, let's just log what we have
        notes = f"{'Pinned' if 'pinned' in tags else ''}"
        
        log_entries.append(f"| 2026-04-29 | {original_id} | {title} | {original_list} | {due} | {dest_list} | Created | Success | {notes} |")
        
    with open(LOG_PATH, "a") as f:
        f.write("\n".join(log_entries) + "\n")
        
    print(f"Appended {len(log_entries)} to {LOG_PATH}")

if __name__ == "__main__":
    main()
