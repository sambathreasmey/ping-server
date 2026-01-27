def has_market_changed(latest_market, issue_name, current_price):
    """
    Returns True if the price string is different for an existing issue.
    """
    # Use commas in print to avoid TypeError if current_price is not a string
    print("issue_name:", issue_name)
    print("current_price:", current_price)

    try:
        if not latest_market:
            return False

        # Build the lookup map
        db_prices = {}
        for item in latest_market:
            if hasattr(item, 'keys'): # Works for sqlite3.Row or dict
                # Convert DB value to string to match your 'current_price' input
                db_prices[str(item['issue_name'])] = str(item['current_price'])
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                db_prices[str(item[0])] = str(item[1])

        # Convert input to string just in case
        input_name = str(issue_name)
        input_price = str(current_price)

        # Comparison logic
        if input_name in db_prices:
            # Direct string comparison: "2,510" != "2510"
            if db_prices[input_name] != input_price:
                print(f"🔄 Change: {input_name} was {db_prices[input_name]}, now {input_price}")
                return True
        
        return False

    except Exception as e:
        print(f"❌ Unexpected error in has_market_changed: {e}")
        return False
