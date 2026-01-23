from itertools import chain
import requests
import os
import datetime
import zoneinfo
from generate import create_card
from price_management import update_if_changed

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SEND_CHAT_ID = os.getenv("SEND_CHAT_ID")
ALLOWED_ISSUE = ['ABC','PWSA']

def is_work_period(dt):
    if dt.weekday() > 4: return False
    return 8 <= dt.hour < 15

def get_khmer_now():
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
    now = datetime.datetime.now(tz)
    
    # Khmer Mappings
    months_kh = {
        "Jan": "មករា", "Feb": "កុម្ភៈ", "Mar": "មីនា", "Apr": "មេសា",
        "May": "ឧសភា", "Jun": "មិថុនា", "Jul": "កក្កដា", "Aug": "សីហា",
        "Sep": "កញ្ញា", "Oct": "តុលា", "Nov": "វិច្ឆិកា", "Dec": "ធ្នូ"
    }
    am_pm_kh = {"AM": "ព្រឹក", "PM": "ល្ងាច"}

    # Get standard parts
    year = now.strftime("%Y")
    month = months_kh[now.strftime("%b")]
    day = now.strftime("%d")
    time_str = now.strftime("%I:%M:%S")
    period = am_pm_kh[now.strftime("%p")]

    # Format: 2026 មករា 22 | 09:27:54 ព្រឹក
    return f"{year} {month} {day} | {time_str} {period}"

def main():
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
    today = datetime.datetime.now(tz)
    
    if not is_work_period(today):
        print("💤 Market is closed.")
        return

    url = "https://csx.com.kh/api/v1/website/home/main-and-growth-board-stocks-trades"
    try:
        response = requests.get(url, params={"lang": "en"}, timeout=30)
        json = response.json()
        data = json['data']
        mainBoardStockTrades = list(chain(
            data.get('mainBoardStockTrades', []),
            data.get('growthBoardStockTrades', [])
        ))
        for mainBoardStockTrade in mainBoardStockTrades:
            issueName = mainBoardStockTrade['issueName'].strip()
            if issueName not in ALLOWED_ISSUE:
                continue
            currentPrice = mainBoardStockTrade['currentPrice']
            change = mainBoardStockTrade['change']
            changeUpDown = mainBoardStockTrade['changeUpDown']
            percentChange = mainBoardStockTrade['percentChange']
            if update_if_changed(issueName, currentPrice):
                print(f"✅ {issueName} Price Changed: {currentPrice}")
                img_path = create_card(issueName, changeUpDown, currentPrice, f"{percentChange}%", change)
                up_down_equal = ""
                # Send to Telegram
                if changeUpDown == "up":
                    up_down_equal = "🔺ឡើង"
                elif changeUpDown == "down":
                    up_down_equal = "🔻ចុះ"
                else:
                    up_down_equal = "▫️ស្មើរ"
                caption = f"<b>{issueName} {currentPrice} រៀល</b> {up_down_equal} {change} | <b>{percentChange}%</b>"
                try:
                    with open(img_path, "rb") as img:
                        response = requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                            data={"chat_id": SEND_CHAT_ID, "caption": caption, "parse_mode": "HTML"},
                            files={"photo": img}
                        )
                        print(f"Telegram response: {response.status_code}")
                finally:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                        print(f"🗑️ Deleted local file: {img_path}")
                
                with open("log.txt", "a", encoding="utf-8", errors="replace") as f:
                    f.write(
                        f"{get_khmer_now()} | "
                        f"{issueName} | "
                        f"Status: {up_down_equal} | "
                        f"Price: {currentPrice} | "
                        f"Change: {change} | "
                        f"ChangePercent: {percentChange}\n"
                    )
            else:
                print(f"🍒 {issueName} No change")

        
        # price_data = data['data']['todayPrice']
        
        # new_price = str(price_data['currentPrice'])
        # change = price_data['change']
        # changePercent = price_data['changePercent']
        # upDown = price_data['changeUpDown']

        # if new_price != abc_tracking:
        #     print(f"✅ Price Changed: {new_price}")
        #     img_path = create_card(upDown, new_price, f"{changePercent}%", change)
        #     up_down_equal = ""
        #     # Send to Telegram
        #     if upDown == "up":
        #         up_down_equal = "🔺ឡើង"
        #     elif upDown == "down":
        #         up_down_equal = "🔻ចុះ"
        #     else:
        #         up_down_equal = "▫️ស្មើរ"
        #     caption = f"<b>ABC {new_price} រៀល</b> {up_down_equal} {change} | <b>{changePercent}%</b>"
        #     try:
        #         with open(img_path, "rb") as img:
        #             response = requests.post(
        #                 f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
        #                 data={"chat_id": SEND_CHAT_ID, "caption": caption, "parse_mode": "HTML"},
        #                 files={"photo": img}
        #             )
        #             print(f"Telegram response: {response.status_code}")
        #     finally:
        #         if os.path.exists(img_path):
        #             os.remove(img_path)
        #             print(f"🗑️ Deleted local file: {img_path}")
            
        #     save_current_price(new_price)
        #     # Log results to file
        #     with open("log.txt", "a") as f:
        #         f.write(f"{get_khmer_now()} | Status: {up_down_equal} | Price: {new_price} | Change: {change} | ChangePercent: {changePercent}\n")
        # else:
        #     print("No price change.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
