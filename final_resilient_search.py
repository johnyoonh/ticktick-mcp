import time
import json
from ticktick_mcp.src.ticktick_client import TickTickClient

def main():
    client = TickTickClient()
    projects = client.get_projects()
    
    target_titles = [
        "Apply to Jobs",
        "Create calendar that is modifiable across calendar accounts",
        "Health calendar",
        "Crypto currency email ca",
        "Organize scanned pdfs and create renamed",
        "California reclaim filing",
        "RDS- PhD Prep Reading books",
        "MCP for Bee",
        "Putting dad’s work into Al",
        "Follow up on lawyers",
        "Complain about BloodLap through Credit card company",
        "Removing dot from johnyoon.h@gmail.com",
        "Cancel Lytt, United Credit Card, Door Dash and Chase Reserve",
        "Eb2 visa (self-petition)",
        "Request removal of lawsuits",
        "Resume a book review",
        "Get better at using Lucidchart",
        "Ask the difference between EKS and ECS",
        "Returns: Costco Online"
    ]
    
    print(f"Total projects: {len(projects)}")
    
    for project in projects:
        pid = project['id']
        name = project['name']
        print(f"Scanning {name} ({pid})...")
        
        data = None
        for attempt in range(5):
            try:
                data = client.get_project_with_data(pid)
                if "error" not in data:
                    break
                print(f"  Attempt {attempt+1} failed: {data['error']}")
            except Exception as e:
                print(f"  Attempt {attempt+1} exception: {e}")
            time.sleep(3)
            
        if not data or "error" in data:
            continue
            
        tasks = data.get("tasks", [])
        for task in tasks:
            task_str = json.dumps(task).lower()
            if "pin" in task_str:
                print(f"FOUND 'pin' in task: {task.get('title')} (Project: {name})")
                print(f"  DATA: {task}")
            
            title = task.get("title", "").lower()
            for target in target_titles:
                if target.lower() in title:
                    print(f"FOUND TARGET: '{task.get('title')}' in '{name}'")
                    print(f"  DATA: {task}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
