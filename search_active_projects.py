import time
import json
from ticktick_mcp.src.ticktick_client import TickTickClient

def fetch_with_retry(client, project_id, project_name, retries=5):
    for attempt in range(retries):
        try:
            data = client.get_project_with_data(project_id)
            if "error" not in data:
                return data
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None

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
    
    active_projects = [p for p in projects if not p.get('closed', False)]
    print(f"Searching in {len(active_projects)} active projects...")
    
    found_count = 0
    for project in active_projects:
        project_id = project['id']
        project_name = project['name']
        
        data = fetch_with_retry(client, project_id, project_name)
        if not data:
            print(f"  FAILED: {project_name}")
            continue
            
        tasks = data.get("tasks", [])
        for task in tasks:
            title = task.get("title", "")
            if any(target.lower() in title.lower() for target in target_titles):
                print(f"FOUND: '{title}' in '{project_name}'")
                print(f"  DATA: {json.dumps(task, indent=2)}")
                found_count += 1
        
        time.sleep(0.5)

    print(f"\nTotal tasks found: {found_count}")

if __name__ == "__main__":
    main()
