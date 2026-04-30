import json
from ticktick_mcp.src.ticktick_client import TickTickClient

client = TickTickClient()
projects = [{'id': 'inbox'}]

found = False
for p in projects:
    project_data = client.get_project_with_data(p['id'])
    for task in project_data.get('tasks', []):
        if task.get('title') == 'Follow up on lawyers':
            print(json.dumps(task, indent=2))
            found = True
            break
    if found: break
