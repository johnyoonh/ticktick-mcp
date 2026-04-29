import json
import os
from ticktick_web_api import TickTickWebClient
from ticktick_mcp.src.ticktick_client import TickTickClient

def main():
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
    
    found_tasks = []
    
    print("Using alternative internal Web API to fetch ALL tasks at once...")
    web_client = TickTickWebClient()
    batch_data = web_client.batch_check(checkpoint=0)
    
    if batch_data and "syncTaskBean" in batch_data:
        all_tasks = batch_data["syncTaskBean"].get("update", [])
        print(f"Fetched {len(all_tasks)} total tasks across all projects/trash/completed.")
        
        for task in all_tasks:
            title = task.get("title")
            if title in target_titles:
                found_tasks.append((title, "Unknown/Batch", task.get("id")))
                print(f"  --> FOUND: '{title}' (ID: {task.get('id')})")
    else:
        print("Failed to fetch data using Web API. Please ensure your Bitwarden vault is unlocked or credentials are set.")
        return

    print("\n--- Summary ---")
    print(f"Found {len(found_tasks)} out of {len(target_titles)} target tasks.")
    
    found_titles = [t[0] for t in found_tasks]
    missing_tasks = [t for t in target_titles if t not in found_titles]
    
    if missing_tasks:
        print("\nMissing Tasks:")
        for t in missing_tasks:
            print(f" - {t}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
