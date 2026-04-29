import json
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
    
    found_tasks = []
    
    # Also create a synthetic 'inbox' project
    all_projects = [{'name': 'Inbox', 'id': 'inbox'}] + projects
    
    for project in all_projects:
        if not project.get('closed', False):
            project_id = project.get('id')
            print(f"Checking project: {project.get('name')} ({project_id})...")
            project_data = client.get_project_with_data(project_id)
            
            if "error" in project_data:
                print(f"  Error fetching data: {project_data['error']}")
                continue
                
            tasks = project_data.get('tasks', [])
            for task in tasks:
                title = task.get('title')
                if title in target_titles:
                    found_tasks.append((title, project.get('name'), task.get('id')))
                    print(f"  --> FOUND: '{title}' (ID: {task.get('id')})")

    print("\n--- Summary ---")
    print(f"Found {len(found_tasks)} out of {len(target_titles)} target tasks.")
    
    found_titles = [t[0] for t in found_tasks]
    missing_tasks = [t for t in target_titles if t not in found_titles]
    
    if missing_tasks:
        print("\nMissing Tasks:")
        for t in missing_tasks:
            print(f" - {t}")

if __name__ == "__main__":
    main()
