import os
import requests
from dotenv import load_dotenv

load_dotenv()

PTERO_URL = os.getenv('PTERO_URL', '').rstrip('/')
PTERO_API_KEY = os.getenv('PTERO_API_KEY')
PTERO_SERVER_ID = os.getenv('PTERO_SERVER_ID')

def get_ptero_headers():
    return {
        "Authorization": f"Bearer {PTERO_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def get_ptero_status() -> str:
    if not PTERO_URL or not PTERO_SERVER_ID or not PTERO_API_KEY:
        return "CONFIG ERROR (Missing Keys)"
    url = f"{PTERO_URL}/api/client/resources/servers/{PTERO_SERVER_ID}/resources"
    try:
        res = requests.get(url, headers=get_ptero_headers(), timeout=5)
        if res.status_code == 200:
            return res.json()['attributes']['current_state'].upper()
        return "OFFLINE / UNREACHABLE"
    except Exception:
        return "OFFLINE / UNREACHABLE"

def send_ptero_power(signal: str):
    if not PTERO_URL or not PTERO_SERVER_ID or not PTERO_API_KEY:
        return False, "❌ Missing Pterodactyl configuration in .env."
    url = f"{PTERO_URL}/api/client/resources/servers/{PTERO_SERVER_ID}/power"
    try:
        res = requests.post(url, headers=get_ptero_headers(), json={"signal": signal}, timeout=5)
        if res.status_code == 204:
            return True, f"🎮 Sent **{signal.upper()}** signal to Minecraft server."
        return False, f"❌ Pterodactyl Error: HTTP {res.status_code}"
    except Exception as e:
        return False, f"❌ Pterodactyl Connection Error: {str(e)}"