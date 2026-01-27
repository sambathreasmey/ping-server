def has_market_changed(latest_market, issue_name, current_price):
    try:
        if not latest_market:
            print("⚠️ latest_market is empty.")
            return False

        # Build the lookup map
        db_prices = {}
        for item in latest_market:
            # We must use EXACT keys from your JSON: "issue_name" and "current_price"
            # We use str() to ensure "1245" matches "1245"
            name = str(item.get("issue_name"))
            price = str(item.get("current_price"))
            db_prices[name] = price

        # Clean strings (remove commas and whitespace)
        search_name = str(issue_name).strip()
        new_price_str = str(current_price).replace(",", "").strip()

        print(f"DEBUG: Checking {search_name}. New Price: {new_price_str}")
        print(f"DEBUG: DB Map: {db_prices}")

        if search_name in db_prices:
            old_price_str = db_prices[search_name].replace(",", "").strip()
            
            if old_price_str != new_price_str:
                print(f"✅ CHANGE DETECTED for {search_name}: {old_price_str} -> {new_price_str}")
                return True
            else:
                print(f"😴 No change for {search_name}.")
        else:
            print(f"❓ {search_name} not found in DB map keys: {list(db_prices.keys())}")
        
        return False

    except Exception as e:
        print(f"❌ Error in has_market_changed: {e}")
        return False
