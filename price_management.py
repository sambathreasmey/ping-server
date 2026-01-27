def has_market_changed(latest_market, issue_name, current_price):
    # Convert inputs to strings and clean them
    issue_name = str(issue_name).strip()
    current_price = str(current_price).strip()

    try:
        if not latest_market:
            return False

        # Build lookup map: { 'ABC': '1245' }
        db_prices = {}
        for item in latest_market:
            # We must use the exact keys from your JSON: 'issue_name' and 'current_price'
            if isinstance(item, dict):
                db_prices[str(item.get('issue_name'))] = str(item.get('current_price'))
            elif hasattr(item, 'keys'): # For sqlite3.Row
                db_prices[str(item['issue_name'])] = str(item['current_price'])

        # DEBUG: See what we are actually comparing
        print(f"Checking for: {issue_name} (New: {current_price})")
        print(f"Database contains: {db_prices}")

        if issue_name in db_prices:
            # Normalize strings by removing commas for a true value comparison
            old_val = db_prices[issue_name].replace(",", "")
            new_val = current_price.replace(",", "")
            
            if old_val != new_val:
                print(f"🔄 Change Detected: {old_val} != {new_val}")
                return True
        else:
            print(f"ℹ️ {issue_name} not found in latest_market, skipping comparison.")
        
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
