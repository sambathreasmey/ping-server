def has_market_changed(latest_market, issue_name, current_price):
    """
    Returns True if the price has changed for an existing issue.
    Returns False if no change or if error occurs.
    """
    try:
        # Check if latest_market is empty
        if not latest_market:
            return False

        # Create lookup map. 
        # We use dict(item) to ensure we can access keys by name
        db_prices = {}
        for item in latest_market:
            # Handle both sqlite3.Row objects and standard dictionaries
            item_dict = dict(item) 
            db_prices[item_dict['issue_name']] = item_dict['current_price']

        # Comparison logic
        if issue_name in db_prices:
            # Check if the price is actually different
            if db_prices[issue_name] != current_price:
                print(f"🔄 Change detected for {issue_name}: {db_prices[issue_name]} -> {current_price}")
                return True
        
        return False

    except KeyError as e:
        print(f"❌ Column name error: {e}. Check if 'issue_name' exists in the query.")
        return False
    except TypeError as e:
        print(f"❌ Data format error: {e}. latest_market elements must be dict-like.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in has_market_changed: {e}")
        return False
