from ticktick_mcp.src.ticktick_client import TickTickClient
import json

def main():
    client = TickTickClient()
    project_id = "67f495b78f08a20343bbc96a" # Inbox-2024
    print(f"Fetching data for project {project_id}...")
    data = client.get_project_with_data(project_id)
    if "error" in data:
        print(f"Error: {data['error']}")
    else:
        print(f"Success! Found {len(data.get('tasks', []))} tasks.")
        for task in data.get('tasks', []):
            print(f"  - {task.get('title')} (SortOrder: {task.get('sortOrder')}, Priority: {task.get('priority')})")

if __name__ == "__main__":
    main()
