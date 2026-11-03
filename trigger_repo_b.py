import os
import requests

def trigger_webhook():
    token = os.environ.get("GITHUB_TOKEN")
    owner = "sambathreasmey"
    repo = "helper_flask_app"
    
    if not token:
        return

    url = f"https://api.github.com/repos/{owner}/{repo}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    payload = {
        "event_type": "run-10s-task"
    }

    try:
        # Fire-and-forget call with a short 5s timeout
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception:
        # Silently ignore all network errors or failures as requested
        pass

if __name__ == "__main__":
    trigger_webhook()
