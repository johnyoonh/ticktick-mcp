import os
import requests
from dotenv import load_dotenv

load_dotenv()
access_token = os.getenv("TICKTICK_ACCESS_TOKEN")

# Test OpenAPI v1 (which we know works)
v1_headers = {
    "Authorization": f"Bearer {access_token}"
}

# Test Internal API v2 with Bearer token
v2_headers = {
    "Authorization": f"Bearer {access_token}"
}

# Test Internal API v2 with Cookie/t header
v2_headers_alt = {
    "Cookie": f"t={access_token}",
    "t": access_token
}

url_v2 = "https://api.ticktick.com/api/v2/batch/check/0"

print("Trying v2 API with Bearer token...")
response = requests.get(url_v2, headers=v2_headers)
print(response.status_code)
if response.status_code == 200:
    print("Success with Bearer token!")
    
print("Trying v2 API with t token...")
response2 = requests.get(url_v2, headers=v2_headers_alt)
print(response2.status_code)
if response2.status_code == 200:
    print("Success with t token!")

