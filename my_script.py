import requests
import datetime
import zoneinfo

def main():
    # Set to your local timezone
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh") 
    now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    url = "https://csx.com.kh/api/v1/website/market-data/stock/prices"
    params = {"lang": "en"}
    
    today = datetime.today()
    
    # toDate = today (YYYYMMDD)
    to_date = today.strftime("%Y%m%d")
    
    def is_work_period(dt: datetime) -> bool:
        if dt.weekday() > 4:  # 0-4 = Mon-Fri
            return False
        # Define allowed time range
        start = time(8, 0)   # 08:00
        end = time(15, 0)    # 15:00
    
        return start <= dt.time() <= end
    
    # fromDate = same day last month (or last valid day of that month)
    year = today.year
    month = today.month - 1
    
    if month == 0:
        month = 12
        year -= 1
    
    last_day_prev_month = calendar.monthrange(year, month)[1]
    day = min(today.day, last_day_prev_month)
    
    from_date_dt = today.replace(year=year, month=month, day=day)
    from_date = from_date_dt.strftime("%Y%m%d")
    
    payload = {
        "fromDate": from_date,
        "toDate": to_date,
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
