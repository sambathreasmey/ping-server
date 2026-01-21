import requests
import datetime
import zoneinfo

def main():
    # Set to your local timezone
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh") 
    now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    url = "https://csx.com.kh/api/v1/website/market-data/stock/prices"
    params = {"lang": "en"}
    payload = {
        "fromDate": "2026-01-20",
        "toDate": "2026-01-21",
        "symbol": "KH1000100003",
        "tradingMethod": "all",
        "board": "main"
    }

    status_log = "Unknown"
    change_log = "N/A"

    try:
        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=30,
        )
        status = response.status_code
        status_log = str(status)

        if response.ok:
            try:
                data = response.json()
                # Accessing the data safely
                today_price = data.get('data', {}).get('todayPrice', {})
                
                changeUpDown = today_price.get('changeUpDown', 'N/A')
                abc_new_tracking = today_price.get('currentPrice', 'N/A')
                change = today_price.get('change', 'N/A')
                changePercent = today_price.get('changePercent', 'N/A')

                print(f"changeUpDown: {changeUpDown}")
                print(f"abc_tracking: {abc_new_tracking}") # Fixed variable name
                print(f"change: {change}")
                print(f"changePercent: {changePercent}")
                
                change_log = str(changeUpDown)
            except ValueError:
                print("Response is not valid JSON")
                status_log = "JSON Error"
        else:
            print(f"Server returned error: {status}")

    except Exception as e:
        status_log = f"Error: {e}"
        print(status_log)

    print(f"Executed at {now} - Status: {status_log}")

    # Log results to file
    with open("log.txt", "a") as f:
        f.write(f"{now} | Status: {status_log} | Change: {change_log}\n")

if __name__ == "__main__":
    main()
