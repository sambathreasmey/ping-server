import requests
import datetime
import zoneinfo

def main():
    # Set to your local timezone
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh") 
    now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    # Sample request: Fetching data from a public API
    try:
        response = requests.get("https://api.github.com")
        status = response.status_code
    except Exception as e:
        status = f"Error: {e}"

    print(f"Executed at {now} - Status: {status}")

    with open("log.txt", "a") as f:
        f.write(f"{now} | Status: {status}\n")

if __name__ == "__main__":
    main()
