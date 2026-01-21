import datetime
import os

def main():
    # Get current time
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Script executed at: {now}")

    # (Optional) Log the execution to a file
    with open("log.txt", "a") as f:
        f.write(f"Executed at {now}\n")

if __name__ == "__main__":
    main()
