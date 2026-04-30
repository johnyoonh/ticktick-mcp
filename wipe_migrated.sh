#!/bin/bash
CLI="/Users/john/repos/mcp-server-apple-events/bin/EventKitCLI"

lists=("⚙️ Automation" "Theology" "Home" "Cleaning" "Shelved")
for list in "${lists[@]}"; do
    data=$("$CLI" --action read --filterList "$list" 2>/dev/null)
    echo "$data" | python3 -c "
import sys, json, subprocess
try:
    data = json.load(sys.stdin)
    for r in data.get('result', {}).get('reminders', []):
        if 'MIGRATION_BATCH' in (r.get('notes') or ''):
            id = r['id']
            print(f'Deleting {r[\"title\"][:30]} from {list}')
            subprocess.run(['$CLI', '--action', 'delete', '--id', id], capture_output=True)
except Exception as e:
    pass
"
done
