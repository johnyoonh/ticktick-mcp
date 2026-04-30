from ticktick_mcp.src.ticktick_client import TickTickClient
import json

def main():
    client = TickTickClient()
    project_id = "65f4ba968bd851059520ff14" # 🦐Cap1
    data = client.get_project_with_data(project_id)
    if "error" in data:
        print(f"Error: {data['error']}")
        return
        
    tasks = data.get("tasks", [])
    print(f"Project: {data['project']['name']}")
    for task in tasks:
        print(f"Task: {task.get('title')}")
        print(f"  Priority: {task.get('priority')}")
        print(f"  SortOrder: {task.get('sortOrder')}")
        print(f"  Tags: {task.get('tags')}")
        # print(f"  All: {task}")
        print("-" * 10)

if __name__ == "__main__":
    main()
