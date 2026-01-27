def has_market_changed(latest_market, issue_name, current_price):
    """
    Returns True if the price has changed for an existing issue.
    """
    try:
        if not latest_market:
            return False

        # Build the lookup map safely
        db_prices = {}
        for item in latest_market:
            # If item is a sqlite3.Row or a dict, this works:
            if hasattr(item, 'keys'):
                db_prices[item['issue_name']] = item['current_price']
            # If item is a plain tuple (issue_name, current_price, timestamp)
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                db_prices[item[0]] = item[1]

        # Comparison logic
        if issue_name in db_prices:
            if db_prices[issue_name] != current_price:
                print(f"🔄 Change: {issue_name} was {db_prices[issue_name]}, now {current_price}")
                return True
        
        return False

    except Exception as e:
        print(f"❌ Unexpected error in has_market_changed: {e}")
        return False
