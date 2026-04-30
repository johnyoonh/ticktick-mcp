import time
from ticktick_mcp.src.ticktick_client import TickTickClient

def fetch_with_retry(client, project_id, project_name, retries=10):
    print(f"Fetching {project_name} ({project_id})...")
    for attempt in range(retries):
        data = client.get_project_with_data(project_id)
        if "error" not in data:
            print(f"  SUCCESS on attempt {attempt+1}!")
            return data
        print(f"  Attempt {attempt+1} failed: {data['error']}")
        time.sleep(5)
    return None

def main():
    client = TickTickClient()
    
    projects_to_check = [
        ("692244b47b70513d1c861a6f", "Resolve"),
        ("692608ce3b87517f7b05a02c", "Followup"),
        ("68a7b734961f91dfd1bc9764", "Seminary"),
        ("6922485f6b3d113d1c8640d5", "Sermon"),
    ]
    
    for pid, name in projects_to_check:
        data = fetch_with_retry(client, pid, name)
        if data:
            tasks = data.get("tasks", [])
            print(f"Found {len(tasks)} tasks in {name}:")
            for task in tasks:
                print(f"  - {task.get('title')}")
        print("-" * 20)

if __name__ == "__main__":
    main()
