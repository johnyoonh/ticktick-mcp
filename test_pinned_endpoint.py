from ticktick_mcp.src.ticktick_client import TickTickClient

def main():
    client = TickTickClient()
    
    # Try a few speculative endpoints
    endpoints = [
        "/task/pinned",
        "/project/pinned",
        "/pinned",
        "/project/all/tasks?filter=pinned",
    ]
    
    for endpoint in endpoints:
        print(f"Trying endpoint: {endpoint}")
        response = client._make_request("GET", endpoint)
        if "error" in response:
            print(f"  Result: Error - {response['error']}")
        else:
            print(f"  Result: Success! Found {len(response)} items.")
            # print(response)

if __name__ == "__main__":
    main()
