import requests
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
    # Sample request: Fetching data from a public API
    try:
        response = requests.post(
            url,
            params=params,
            json=payload,
            timeout=30,
        )
        status = response.status_code
        try:
            data = response.json()
            changeUpDown = data['data']['todayPrice']['changeUpDown']
            print("changeUpDown: ", changeUpDown)
            abc_new_tracking = data['data']['todayPrice']['currentPrice']
            print("abc_tracking: ", abc_tracking)
            change = data['data']['todayPrice']['change']
            print("change: ", change)
            changePercent = data['data']['todayPrice']['changePercent']
            print("changePercent: ", changePercent)
        except ValueError:
            print("Response is not valid JSON")
    except Exception as e:
        status = f"Error: {e}"

    print(f"Executed at {now} - Status: {status}")

    with open("log.txt", "a") as f:
        f.write(f"{now} | Status: {status}\n")
        f.write(f"{now} | Status: {changeUpDown}\n")

if __name__ == "__main__":
    main()
