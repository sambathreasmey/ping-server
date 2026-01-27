import json

def has_market_changed(latest_market, issue_name, current_price):
    try:
        # --- THE FIX: Convert string to list if necessary ---
        if isinstance(latest_market, str):
            latest_market = json.loads(latest_market)
        
        if not latest_market:
            return False

        # Build the lookup map
        db_prices = {}
        for item in latest_market:
            # item is now a dictionary, so .get() will work
            name = str(item.get("issue_name"))
            price = str(item.get("current_price"))
            db_prices[name] = price

        # Clean strings for comparison
        search_name = str(issue_name).strip()
        new_price_str = str(current_price).replace(",", "").strip()

        if search_name in db_prices:
            old_price_str = db_prices[search_name].replace(",", "").strip()
            
            if old_price_str != new_price_str:
                print(f"✅ CHANGE: {search_name} ({old_price_str} -> {new_price_str})")
                return True
        else:
            # If it's a brand new item, we should probably return True to save it
            print(f"🆕 NEW ITEM: {search_name}")
            return True 
        
        return False

    except Exception as e:
        print(f"❌ Error in has_market_changed: {e}")
        return False
