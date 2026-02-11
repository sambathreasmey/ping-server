import time

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    try:
        push_telegram()
    except Exception as e:
        print(f"Error: {e}")

def push_telegram():
    time.sleep(20)

if __name__ == "__main__":
    main()
