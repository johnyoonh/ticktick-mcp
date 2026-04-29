import os
import json
import requests
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class TickTickWebClient:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("TICKTICK_USERNAME")
        self.password = os.getenv("TICKTICK_PASSWORD")
        
        self.ticktick_server = "ticktick.com"
        self.protocol = "https://"
        self.api_protocol = "https://api."
        self.api_version = "/api/v2"
        
        self.api_url = f"{self.api_protocol}{self.ticktick_server}{self.api_version}"
        self.login_url = f"{self.protocol}{self.ticktick_server}{self.api_version}"
        
        self.token = None
        self.inbox_id = None
        self.cookie_header = ""
        self.cookies = {}
        
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        self.x_device = '{"platform":"web","os":"Mac OS X","device":"Chrome 124.0.0.0","name":"","version":6070,"id":"web_random_id","channel":"website","campaign":"","websocket":""}'

    def login(self):
        if not self.username or not self.password:
            logger.error("TICKTICK_USERNAME and TICKTICK_PASSWORD must be set in .env")
            return False
            
        url = f"{self.login_url}/user/signon?wc=true&remember=true"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-device": self.x_device,
            "User-Agent": self.user_agent,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"Login failed: {response.status_code}")
            return False
            
        data = response.json()
        self.token = data.get("token")
        self.inbox_id = data.get("inboxId")
        
        # Extract cookies
        self.cookies = response.cookies.get_dict()
        cookie_parts = [f"{k}={v}" for k, v in self.cookies.items()]
        self.cookie_header = "; ".join(cookie_parts) + ";"
        
        return True
        
    def batch_check(self, checkpoint=0):
        if not self.token:
            if not self.login():
                return None
                
        url = f"{self.api_url}/batch/check/{checkpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "x-device": self.x_device,
            "Cookie": f"t={self.token}; {self.cookie_header}",
            "t": self.token
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get tasks: {response.status_code}")
            return None
            
        return response.json()
