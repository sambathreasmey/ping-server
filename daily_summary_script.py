def main():
    try:
        push_telegram()
    except Exception as e:
        print(f"Error: {e}")

def push_telegram():
    print("Pushed to telegram bot.")

if __name__ == "__main__":
    main()