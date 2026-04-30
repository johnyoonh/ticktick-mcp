import subprocess
import json
import time
from pathlib import Path

def main():
    batch_count = 1
    total_migrated = 0
    
    while True:
        print(f"--- Starting Batch {batch_count} ---")
        
        # Run prepare_batch.py
        subprocess.run(["python", "prepare_batch.py"], check=True)
        
        batch_file = Path("next_batch.json")
        if not batch_file.exists():
            print("No next_batch.json found. Stopping.")
            break
            
        with open(batch_file, "r") as f:
            tasks = json.load(f)
            
        if not tasks:
            print("No tasks remaining to migrate. Migration complete!")
            break
            
        # Run migrate_next_batch.py to execute the migration
        res = subprocess.run(["python", "migrate_next_batch.py"])
        if res.returncode != 0:
            print(f"Error executing batch {batch_count}. Stopping to avoid infinite loops.")
            break
            
        total_migrated += len(tasks)
        print(f"Batch {batch_count} complete. Total migrated so far: {total_migrated}\n")
        batch_count += 1
        
        # Small sleep to let the system breathe
        time.sleep(2)

if __name__ == "__main__":
    main()
