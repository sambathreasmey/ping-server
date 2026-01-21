import datetime
import zoneinfo

def main():
    tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh") 
    now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Script executed at (Local Time): {now}")

    with open("log.txt", "a") as f:
        f.write(f"Executed at {now}\n")

if __name__ == "__main__":
    main()
