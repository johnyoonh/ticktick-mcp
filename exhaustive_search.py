import time
from ticktick_mcp.src.ticktick_client import TickTickClient

def main():
    client = TickTickClient()
    projects = client.get_projects()
    
    if "error" in projects:
        print(f"Error fetching projects: {projects['error']}")
        return

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
    
    found_count = 0
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        
        print(f"Checking project: {project_name} ({project_id})...")
        
        data = None
        for attempt in range(3):
            data = client.get_project_with_data(project_id)
            if "error" not in data:
                break
            print(f"  Attempt {attempt+1} failed: {data['error']}")
            time.sleep(2)
            
        if not data or "error" in data:
            print(f"  FAILED to fetch data for {project_name}")
            continue
            
        tasks = data.get("tasks", [])
        for task in tasks:
            title = task.get("title", "")
            if any(target.lower() == title.lower() for target in target_titles):
                print(f"FOUND: '{title}' in '{project_name}'")
                print(f"  DATA: {task}")
                found_count += 1
            elif any(target.lower() in title.lower() for target in target_titles):
                # Partial match
                print(f"PARTIAL MATCH: '{title}' in '{project_name}'")
                # print(f"  DATA: {task}")
        
        time.sleep(1) # Delay between projects

    print(f"\nTotal tasks found: {found_count} out of {len(target_titles)}")

if __name__ == "__main__":
    main()
