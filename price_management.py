import json

def has_market_changed(latest_market, issue_name, current_price):
    try:
        # Ensure latest_market is a list/dict, not a raw string
        if isinstance(latest_market, str):
            latest_market = json.loads(latest_market)
        
        if not latest_market:
            return True # Return True to allow inserting first-ever data

        # Build lookup: { 'ABC': '1245' }
        db_prices = {str(item.get("issue_name")): str(item.get("current_price")) for item in latest_market}

        search_name = str(issue_name).strip()
        # Clean commas for a "pure" string comparison (e.g., "7,160" -> "7160")
        new_price_str = str(current_price).replace(",", "").strip()

        if search_name in db_prices:
            old_price_str = db_prices[search_name].replace(",", "").strip()
            
            if old_price_str != new_price_str:
                return True # Price is different
        else:
            return True # Item is new
        
        return False # No change

    except Exception as e:
        print(f"❌ Error in has_market_changed: {e}")
        return False
